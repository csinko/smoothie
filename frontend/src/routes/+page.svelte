<script lang="ts">
  export let data: { smoothies: any[] }; // Smoothies now include pre-loaded macros from the server

  function generateMacroBar(ingredients, totalCalories) {
    const colors = { protein: "bg-blue-600", fat: "bg-yellow-400", carbs: "bg-green-500" };
    const macroTotals = { protein: 0, fat: 0, carbs: 0 };

    let barHtml = '<div class="flex flex-col w-full">';

    for (const macro of ["protein", "fat", "carbs"]) {
      const macroCalories = ingredients.reduce((sum, ingredient) => 
        sum + ingredient[macro] * (macro !== "fat" ? 4 : 9), 0);
      macroTotals[macro] = macroCalories;
      const percentage = (macroCalories / totalCalories) * 100;
      const totalGrams = ingredients.reduce((sum, ingredient) => sum + ingredient[macro], 0);

      barHtml += `<div class="mb-2"><p class="font-medium">${macro.charAt(0).toUpperCase() + macro.slice(1)}: ${macroCalories.toFixed(1)} calories (${percentage.toFixed(1)}%) - ${totalGrams.toFixed(1)}g</p>`;
      barHtml += `<div class="relative h-6 rounded-full overflow-hidden bg-gray-200">`;

      let cumulativePercentage = 0;
      for (const ingredient of ingredients) {
        const ingredientMacro = ingredient[macro];
        const ingredientCalories = ingredientMacro * (macro !== "fat" ? 4 : 9);
        const ingredientPercentage = (ingredientCalories / totalCalories) * 100;

        barHtml += `<div class="${colors[macro]} h-full absolute" style="left: ${cumulativePercentage}%; width: ${ingredientPercentage}%;" title="${ingredient.name}: ${ingredientMacro.toFixed(1)}g (${ingredientCalories.toFixed(1)} calories)"></div>`;
        cumulativePercentage += ingredientPercentage;
      }

      cumulativePercentage = 0;
      for (const ingredient of ingredients) {
        const ingredientMacro = ingredient[macro];
        const ingredientCalories = ingredientMacro * (macro !== "fat" ? 4 : 9);
        const ingredientPercentage = (ingredientCalories / totalCalories) * 100;
        cumulativePercentage += ingredientPercentage;
        if (cumulativePercentage < 100) {
          const darkerColor = colors[macro].replace(/\d+$/, (match) => Math.min(parseInt(match) + 200, 900));
          barHtml += `<div class="h-full w-0.5 ${darkerColor} absolute z-10" style="left: ${cumulativePercentage}%;"></div>`;
        }
      }

      barHtml += "</div></div>";
    }

    barHtml += "</div>";
    return barHtml;
  }

  async function handleIngredientChange(smoothieIndex: number, ingredientIndex: number, newValue: string) {
    console.log(`Smoothie ${smoothieIndex + 1}, Ingredient ${ingredientIndex + 1} modified:`, newValue);
    
    // Update the ingredient in the data
    data.smoothies[smoothieIndex].ingredients[ingredientIndex] = newValue;
  
    // Call the API to recalculate macros
    try {
      const response = await fetch('http://localhost:8000/calculate-macros', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients: data.smoothies[smoothieIndex].ingredients }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch macros');
      }
  
      const newMacros = await response.json();
  
      // Update the macros for the smoothie
      data.smoothies[smoothieIndex].macros = newMacros;
    } catch (error) {
      console.error('Error updating macros:', error);
    }
  }

</script>

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
    {#if data.smoothies.length > 0}
      {#each data.smoothies as smoothie, smoothieIndex}
        <div class="mb-16">
          <h2 class="text-2xl font-semibold text-green-700 mb-4">{smoothie.title}</h2>
          <img src={"http://localhost:8000/" + smoothie.image} alt={smoothie.title} class="w-full max-w-sm mx-auto rounded-lg shadow-md mb-4">
          <h3 class="text-xl font-medium text-green-600 mb-2">Ingredients:</h3>
          <div class="space-y-1">
            {#each smoothie.ingredients as ingredient, index}
              <div>
                <input
                  type="text"
                  value={ingredient}
                  class="w-full p-1 border rounded"
                  on:blur={(e) => handleIngredientChange(smoothieIndex, index, e.target.value)}
                />
              </div>
            {/each}
          </div>
          {#if smoothie.macros}
            <h3 class="text-xl font-medium text-green-600 mt-4 mb-2">Macronutrients:</h3>
            <div class="bg-green-50 p-4 rounded-lg">
              <p class="text-lg mb-2">Total Calories: {smoothie.macros.macros.calories}</p>
              {@html generateMacroBar(smoothie.macros.ingredients, smoothie.macros.macros.calories)}
            </div>
          {/if}
          {#if smoothie.why}
            <p class="text-lg mt-4"><strong>Why:</strong> {smoothie.why}</p>
          {/if}
        </div>
      {/each}
    {:else}
      <p>Loading smoothies...</p>
    {/if}
  </section>

  <!-- Footer -->
  <footer class="bg-green-100 py-8">
    <div class="max-w-5xl mx-auto text-center">
      <p class="text-gray-600">Cam Sinko</p>
    </div>
  </footer>

</body>
</html>

