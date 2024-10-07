# Smoothie API and Frontend

This project consists of a FastAPI backend API and a Svelte frontend that serves smoothie recipes. It uses Nix for package management and environment setup.

## Project Structure

```
.
├── .github/workflows/build.yml
├── .gitignore
├── api.py               # FastAPI backend
├── assets/              # Image assets for the smoothies
├── flake.lock
├── flake.nix           # Nix configuration file
├── frontend/            # Frontend application
│   ├── .gitignore
│   ├── .npmrc
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── README.md
│   ├── eslint.config.js
│   ├── package-lock.json
│   ├── package.json
│   ├── src/             # Frontend source code
│   │   ├── app.d.ts
│   │   ├── app.html
│   │   ├── lib/
│   │   ├── routes/
│   │   └── static/
│   └── vite.config.ts
├── index.html           # HTML entry point for the frontend
├── ingredients.json     # Ingredient data
├── recipes.json         # Recipe data
└── render.py            # Rendering script (if applicable)

## Prerequisites

Ensure you have [Nix](https://nixos.org/download.html) installed on your system.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Enter the Nix Development Environment**
   Run the following command to enter the Nix development environment:
   ```bash
   nix develop
   ```

3. **Install Frontend Dependencies**
   Navigate to the `frontend` directory and install the necessary npm packages:
   ```bash
   cd frontend
   npm install
   ```

4. **Run the Frontend Development Server**
   Start the frontend development server with:
   ```bash
   npm run dev
   ```

5. **Run the FastAPI Backend**
   Open a new terminal tab/window, navigate back to the project root, and run the FastAPI backend using Uvicorn:
   ```bash
   uvicorn api:app --reload
   ```

6. **Access the Application**
   - Frontend: Open your browser and navigate to `http://localhost:3000`
   - API: The FastAPI backend will be running on `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.


## Additional Notes

- The Nix environment provides all necessary dependencies for both Python and Node.js, so no further installations are required.
- The assets for the smoothies are located in the `assets/` directory and are served through the FastAPI application.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
