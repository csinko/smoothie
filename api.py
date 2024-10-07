import json
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from pathlib import Path
from subprocess import run, CalledProcessError

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from starlette.responses import FileResponse


WEBP_QUALITY = 80  # Quality level of compressed webp files
COMPRESSED_SUFFIX = "_compressed.webp"
FORCE_RECOMPRESS = True


def compress_webp_file(
    src_path: Path, quality: int = WEBP_QUALITY, width: int = 500, height: int = 500
) -> Path:
    """
    Compresses a webp file using cwebp, resizes it, and stores it with a compressed suffix.

    Args:
        src_path (Path): The path to the source .webp file.
        quality (int): The quality setting for cwebp (default 80).
        width (int): The desired width of the image after resizing.
        height (int): The desired height of the image after resizing.

    Returns:
        Path: The path to the compressed and resized .webp file.
    """
    compressed_path = src_path.with_name(src_path.stem + COMPRESSED_SUFFIX)

    # Only compress if the compressed file does not already exist
    if compressed_path.exists():
        if FORCE_RECOMPRESS:
            logger.info(
                f"Recompressing file {src_path} to {compressed_path} ({width}x{height})"
            )
            compressed_path.unlink()
        else:
            logger.info(f"Compressed file already exists: {compressed_path}")
            return compressed_path

    logger.info(
        f"Compressing and resizing {src_path} to {compressed_path} ({width}x{height})"
    )

    # Using subprocess to call cwebp for compression and resizing
    try:
        run(
            [
                "cwebp",
                "-q",
                str(quality),
                "-resize",
                str(width),
                str(height),
                str(src_path),
                "-o",
                str(compressed_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(
            f"Successfully compressed and resized {src_path} -> {compressed_path}"
        )
    except CalledProcessError as e:
        logger.error(f"Compression and resizing failed for {src_path}: {e.stderr}")
        raise

    return compressed_path


def compress_webp_files_in_directory(
    directory: Path, quality: int = WEBP_QUALITY
) -> None:
    """
    Walks through a directory and compresses all .webp files.

    Args:
        directory (Path): The directory to scan for .webp files.
        quality (int): The quality setting for cwebp (default 80).
    """
    # Using rglob to recursively find all .webp files
    webp_files = directory.rglob("*.webp")
    for webp_file in webp_files:
        if not webp_file.name.endswith(
            COMPRESSED_SUFFIX
        ):  # Avoid compressing already compressed files
            compress_webp_file(webp_file, quality)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = app  # Unused
    # Pre-compress WebP files during startup
    assets_directory = Path("./assets")

    if assets_directory.is_dir():
        logger.info(f"Compressing .webp files in {assets_directory} on startup.")
        compress_webp_files_in_directory(assets_directory)
    else:
        logger.error(f"Assets directory {assets_directory} does not exist.")

    yield  # This is where the app runs

    # Add any necessary cleanup here if needed


# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the ingredient descriptions from the ingredients.json file
with open("ingredients.json", "r") as f:
    ingredients_data = json.load(f)

with open("recipes.json", "r") as f:
    smoothies_data = json.load(f)


@dataclass
class Smoothie:
    title: str
    image: str
    ingredients: list[str]
    why: str | None = None


@dataclass
class Ingredient:
    name: str
    amount: float
    amount_str: str
    unit: str
    calories: float
    protein: float
    fat: float
    carbs: float
    description: str | None = None

    @classmethod
    def from_string(cls, ingredient_string: str, ingredients_data: dict):
        parts = ingredient_string.split()
        amount = parts[0]

        # Logic to handle unit or whole ingredients
        if len(parts) > 1 and (
            parts[1] in ["tsp", "tbsp", "cup", "whole"] or parts[1].isdigit()
        ):
            unit = parts[1]
            name = " ".join(parts[2:])
        else:
            unit = "whole"
            name = " ".join(parts[1:])

        # Check if the ingredient exists in the data
        if name not in ingredients_data:
            raise ValueError(f"Ingredient '{name}' not found in ingredients data")

        ingredient_data = ingredients_data[name]
        multiplier = cls._calculate_multiplier(amount, unit)

        return cls(
            name=name,
            amount=eval(amount) if "/" in amount else float(amount),
            amount_str=amount,
            unit=unit,
            calories=ingredient_data["calories"] * multiplier,
            protein=ingredient_data["protein"] * multiplier,
            fat=ingredient_data["fat"] * multiplier,
            carbs=ingredient_data["carbohydrates"] * multiplier,
            description=ingredient_data.get("description"),
        )

    @staticmethod
    def _calculate_multiplier(amount: str, unit: str) -> float:
        if unit in ["tsp", "tbsp"]:
            return 1 / 48 if unit == "tsp" else 1 / 16
        elif unit == "cup":
            return eval(amount) if "/" in amount else float(amount)
        elif unit == "whole" or unit.isdigit():
            return eval(amount) if "/" in amount else float(amount)
        else:
            return 1.0


# Custom Pydantic type for Ingredient parsing
class IngredientType(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # Parse the ingredient string into an Ingredient object
        try:
            return Ingredient.from_string(value, ingredients_data)
        except ValueError as e:
            raise ValueError(f"Error parsing ingredient: {e}")


class IngredientStringsRequest(BaseModel):
    ingredients: list[
        Ingredient
    ]  # Automatically parse into a list of Ingredient objects

    @validator("ingredients", pre=True, each_item=True)
    def parse_ingredient(cls, value: str) -> Ingredient:
        print(f"Parsing raw ingredient: {value}")
        if isinstance(value, str):
            return Ingredient.from_string(
                value, ingredients_data
            )  # Use Ingredient's from_string method
        return value


# FastAPI app
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint to calculate macros from ingredient strings
@app.post("/calculate-macros")
def calculate_macros(request: IngredientStringsRequest):
    total_macros = {
        "calories": sum(i.calories for i in request.ingredients),
        "protein": sum(i.protein for i in request.ingredients),
        "fat": sum(i.fat for i in request.ingredients),
        "carbs": sum(i.carbs for i in request.ingredients),
    }

    return {
        "macros": {k: round(v, 1) for k, v in total_macros.items()},
        "ingredients": [i.__dict__ for i in request.ingredients],
    }


@app.get("/smoothies")
def get_smoothies():
    smoothies = [Smoothie(**smoothie) for smoothie in smoothies_data["smoothies"]]
    return smoothies


class CustomStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        # Convert path to Path object for easier manipulation
        assert self.directory is not None
        requested_path = Path(self.directory) / path

        # Check if the request is for a .webp file and if the compressed version exists
        if requested_path.suffix == ".webp":
            compressed_path = requested_path.with_name(
                requested_path.stem + "_compressed.webp"
            )
            if compressed_path.exists():
                logger.info(f"Serving compressed WebP file: {compressed_path}")
                return FileResponse(compressed_path)
            else:
                logger.info(f"Serving original WebP file: {requested_path}")

        # Fallback to default behavior (serving the original file)
        return await super().get_response(path, scope)


# Mount the custom static files handler
app.mount("/assets", CustomStaticFiles(directory="assets"), name="assets")


# Custom handler for validation errors (422 Unprocessable Entity)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the full request and error details
    logger.error(f"Validation error for request: {request.method} {request.url}")
    logger.error(f"Request body: {await request.body()}")
    logger.error(f"Validation errors: {exc.errors()}")

    # Process the errors to ensure JSON serializability
    error_details = [
        {
            "loc": e["loc"],
            "msg": e["msg"],
            "type": e["type"],
            "ctx": {"error": str(e["ctx"]["error"])}
            if "ctx" in e and isinstance(e["ctx"]["error"], Exception)
            else e.get("ctx"),
        }
        for e in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"detail": error_details, "body": exc.body},
    )


# Run with: uvicorn api:app --reload
