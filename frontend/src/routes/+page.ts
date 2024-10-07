import type { PageLoad } from './$types';

async function fetchMacros(fetch, ingredients) {
  const response = await fetch('http://localhost:8000/calculate-macros', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ ingredients }),
  });
  return await response.json();
}

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch('http://localhost:8000/smoothies');
  const smoothies = await response.json();

  // Fetch macros for each smoothie
  for (let smoothie of smoothies) {
    smoothie.macros = await fetchMacros(fetch, smoothie.ingredients);
  }

  return {
    smoothies,
  };
};

