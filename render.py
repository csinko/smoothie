import json
from dataclasses import dataclass
from typing import Optional


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
    description: Optional[str] = None

    @classmethod
    def from_string(cls, ingredient_string: str, ingredients_data: dict):
        parts = ingredient_string.split()
        amount = parts[0]

        if len(parts) > 1 and (
            parts[1] in ["tsp", "tbsp", "cup", "whole"] or parts[1].isdigit()
        ):
            unit = parts[1]
            name = " ".join(parts[2:])
        else:
            unit = "whole"
            name = " ".join(parts[1:])

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


def calculate_macros(ingredients):
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    for ingredient in ingredients:
        total_calories += ingredient.calories
        total_protein += ingredient.protein
        total_fat += ingredient.fat
        total_carbs += ingredient.carbs

        # Print macros for each ingredient
        print(f"Ingredient: {ingredient.name}")
        print(f"  Parsed amount: {ingredient.amount} {ingredient.unit}")
        print(f"  Calories: {ingredient.calories:.1f}")
        print(f"  Protein: {ingredient.protein:.1f}g")
        print(f"  Fat: {ingredient.fat:.1f}g")
        print(f"  Carbs: {ingredient.carbs:.1f}g")
        print()

    return {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1),
    }


def generate_macro_bar(ingredients, total_calories):
    bar_html = '<div class="flex flex-col w-full">'
    colors = {"protein": "bg-blue-600", "fat": "bg-yellow-400", "carbs": "bg-green-500"}
    macro_totals = {"protein": 0, "fat": 0, "carbs": 0}

    def darken_color(color, amount=200):
        # Extract the color number from the Tailwind class
        base = int(color.split("-")[-1])
        # Calculate the darker shade (minimum 900)
        darker = min(base + amount, 900)
        # Return the new color class
        return f"{color.rsplit('-', 1)[0]}-{darker}"

    for macro in ["protein", "fat", "carbs"]:
        macro_calories = sum(
            getattr(ingredient, macro) * (4 if macro != "fat" else 9)
            for ingredient in ingredients
        )
        macro_totals[macro] = macro_calories
        percentage = (macro_calories / total_calories) * 100

        bar_html += f'<div class="mb-2"><p class="font-medium">{macro.capitalize()}: {macro_totals[macro]:.1f} calories ({percentage:.1f}%) - {sum(getattr(ingredient, macro) for ingredient in ingredients):.1f}g</p>'
        bar_html += (
            f'<div class="relative h-6 rounded-full overflow-hidden bg-gray-200">'
        )

        cumulative_percentage = 0
        for ingredient in ingredients:
            ingredient_macro = getattr(ingredient, macro)
            ingredient_calories = ingredient_macro * (4 if macro != "fat" else 9)
            ingredient_percentage = (ingredient_calories / total_calories) * 100

            bar_html += f'<div class="{colors[macro]} h-full absolute" style="left: {cumulative_percentage}%; width: {ingredient_percentage}%;" title="{ingredient.name}: {ingredient_macro:.1f}g ({ingredient_calories:.1f} calories)"></div>'
            cumulative_percentage += ingredient_percentage

        # Add darker divider lines on top
        cumulative_percentage = 0
        for ingredient in ingredients:
            ingredient_macro = getattr(ingredient, macro)
            ingredient_calories = ingredient_macro * (4 if macro != "fat" else 9)
            ingredient_percentage = (ingredient_calories / total_calories) * 100
            cumulative_percentage += ingredient_percentage
            if cumulative_percentage < 100:
                darker_color = darken_color(colors[macro])
                bar_html += f'<div class="h-full w-0.5 {darker_color} absolute z-10" style="left: {cumulative_percentage}%;"></div>'

        bar_html += "</div></div>"

    bar_html += "</div>"
    return bar_html, macro_totals


# Load the smoothie data from the recipes.json file
with open("recipes.json", "r") as f:
    smoothies_data = json.load(f)

# Load the ingredient descriptions from the ingredients.json file
with open("ingredients.json", "r") as f:
    ingredients_data = json.load(f)

# Start building the HTML content with a basic structure
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Gut-Healing Smoothie Recipes</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Inter', sans-serif;
    }
    h1, h2 {
      font-family: 'Playfair Display', serif;
    }
  </style>
</head>
<body class="bg-white text-gray-800">

  <!-- Header -->
  <header class="bg-green-50 py-8">
    <div class="max-w-5xl mx-auto text-center">
      <h1 class="text-4xl font-semibold text-green-700">7 Gut-Healing Smoothie Recipes</h1>
      <p class="text-lg mt-4 text-green-600">Boost your gut health with these nourishing and delicious smoothies.</p>
    </div>
  </header>

  <!-- Introduction -->
  <section class="max-w-4xl mx-auto px-4 py-12">
    <p class="text-lg mb-8">
      These smoothies are designed to support gut health by balancing the gut microbiome, reducing inflammation, 
      and promoting the growth of beneficial bacteria such as <em>Bifidobacteria</em> and <em>Lactobacillus</em>. 
      If you're experiencing issues like gas, irregular bowel movements, or energy dips after meals, 
      these smoothies can help address potential gut dysbiosis and promote overall digestive health. 
      They are rich in prebiotics, probiotics, fiber, and polyphenols—key nutrients to target harmful bacteria like <em>Bacteroides</em>, 
      while boosting beneficial microbes to support digestion, energy, and immunity.
    </p>
  </section>

  <!-- Content Section -->
  <section class="max-w-4xl mx-auto px-4 py-12">
"""

# Loop through each smoothie in the JSON and append its HTML structure
for smoothie in smoothies_data["smoothies"]:
    print(f"Calculating macros for {smoothie['title']}...")

    # Parse ingredients once
    parsed_ingredients = [
        Ingredient.from_string(ingredient_string, ingredients_data)
        for ingredient_string in smoothie["ingredients"]
    ]

    macros = calculate_macros(parsed_ingredients)
    total_macros = macros["protein"] + macros["fat"] + macros["carbs"]

    smoothie_html = f"""
    <div class="mb-16">
      <h2 class="text-2xl font-semibold text-green-700 mb-4">{smoothie['title']}</h2>
      <img src="{smoothie['image']}" alt="{smoothie['title']}" class="w-full max-w-sm mx-auto rounded-lg shadow-md mb-4">
      <h3 class="text-xl font-medium text-green-600 mb-2">Ingredients:</h3>
      <ul class="list-disc list-inside text-lg">
    """

    # Add ingredients as list items with descriptions if available in the ingredients.json file
    for ingredient in parsed_ingredients:
        smoothie_html += f"<li><strong>{ingredient.amount_str} {ingredient.unit} {ingredient.name}</strong>"
        if ingredient.description:
            smoothie_html += f" (<em>{ingredient.description}</em>)"
        smoothie_html += "</li>\n"

    smoothie_html += f"""
      </ul>
             <h3 class="text-xl font-medium text-green-600 mt-4 mb-2">Macronutrients:</h3>
             <div class="bg-green-50 p-4 rounded-lg">
               <p class="text-lg mb-2">Total Calories: {macros['calories']}</p>
               {generate_macro_bar(parsed_ingredients, macros['calories'])[0]}
             </div>
      <p class="text-lg mt-4"><strong>Why:</strong> {smoothie['why']}</p>
    </div>
    """

    # Append the smoothie content to the main HTML content
    html_content += smoothie_html

# Close the HTML structure
html_content += """
  </section>

  <!-- Footer -->
  <footer class="bg-green-100 py-8">
    <div class="max-w-5xl mx-auto text-center">
      <p class="text-gray-600">Cam Sinko</p>
    </div>
  </footer>

</body>
</html>
"""

# Save the generated HTML content to a file
with open("index.html", "w") as html_file:
    html_file.write(html_content)

print("HTML file generated successfully!")
