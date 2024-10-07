import json


def calculate_macros(ingredients, ingredients_data):
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    for ingredient_string in ingredients:
        parts = ingredient_string.split()
        amount = parts[0]

        # Check if the second part is a valid unit or a number
        if len(parts) > 1 and (
            parts[1] in ["tsp", "tbsp", "cup", "whole"] or parts[1].isdigit()
        ):
            unit = parts[1]
            name = " ".join(parts[2:])
        else:
            unit = "whole"
            name = " ".join(parts[1:])

        if name in ingredients_data:
            ingredient = ingredients_data[name]
            multiplier = 1

            if unit in ["tsp", "tbsp"]:
                # Convert tsp and tbsp to cups
                multiplier = 1 / 48 if unit == "tsp" else 1 / 16
            elif unit == "cup":
                multiplier = eval(amount) if "/" in amount else float(amount)
            elif unit == "whole" or unit.isdigit():
                multiplier = eval(amount) if "/" in amount else float(amount)

            calories = ingredient["calories"] * multiplier
            protein = ingredient["protein"] * multiplier
            fat = ingredient["fat"] * multiplier
            carbs = ingredient["carbohydrates"] * multiplier

            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs

            # Print macros for each ingredient
            print(f"Ingredient: {ingredient_string}")
            print(f"  Parsed amount: {multiplier} cup(s)")
            print(f"  Calories: {calories:.1f}")
            print(f"  Protein: {protein:.1f}g")
            print(f"  Fat: {fat:.1f}g")
            print(f"  Carbs: {carbs:.1f}g")
            print()

    return {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1),
    }


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
    macros = calculate_macros(smoothie["ingredients"], ingredients_data)
    total_macros = macros["protein"] + macros["fat"] + macros["carbs"]

    smoothie_html = f"""
    <div class="mb-16">
      <h2 class="text-2xl font-semibold text-green-700 mb-4">{smoothie['title']}</h2>
      <img src="{smoothie['image']}" alt="{smoothie['title']}" class="w-full max-w-sm mx-auto rounded-lg shadow-md mb-4">
      <h3 class="text-xl font-medium text-green-600 mb-2">Ingredients:</h3>
      <ul class="list-disc list-inside text-lg">
    """

    # Add ingredients as list items with descriptions if available in the ingredients.json file
    for ingredient_string in smoothie["ingredients"]:
        parts = ingredient_string.split()
        amount = parts[0]

        # Check if the second part is a valid unit or a number
        if len(parts) > 1 and (
            parts[1] in ["tsp", "tbsp", "cup", "whole"] or parts[1].isdigit()
        ):
            unit = parts[1]
            name = " ".join(parts[2:])
        else:
            unit = "whole"
            name = " ".join(parts[1:])

        description = ingredients_data.get(name, {}).get("description", "")
        smoothie_html += f"<li><strong>{ingredient_string}</strong>"
        if description:
            smoothie_html += f" (<em>{description}</em>)"
        smoothie_html += "</li>\n"

    smoothie_html += f"""
      </ul>
      <h3 class="text-xl font-medium text-green-600 mt-4 mb-2">Macronutrients:</h3>
      <div class="bg-green-50 p-4 rounded-lg">
        <p class="text-lg mb-2">Total Calories: {macros['calories']}</p>
        <div class="flex justify-between mb-2">
          <span>Protein: {macros['protein']}g ({round(macros['protein']/total_macros*100, 1)}%)</span>
          <span>Fat: {macros['fat']}g ({round(macros['fat']/total_macros*100, 1)}%)</span>
          <span>Carbs: {macros['carbs']}g ({round(macros['carbs']/total_macros*100, 1)}%)</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
          <div class="bg-blue-600 h-2.5 rounded-full" style="width: {round(macros['protein']/total_macros*100, 1)}%"></div>
          <div class="bg-yellow-400 h-2.5 rounded-full" style="width: {round(macros['fat']/total_macros*100, 1)}%"></div>
          <div class="bg-green-500 h-2.5 rounded-full" style="width: {round(macros['carbs']/total_macros*100, 1)}%"></div>
        </div>
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
