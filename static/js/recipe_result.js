function getRecipes() {
    let ingredients = document.getElementById('ingredients').value;
    fetch('/recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients: ingredients }),
    })
    .then(response => response.json())
    .then(data => displayRecipes(data));
}

function displayRecipes(data) {
    let recipesDiv = document.getElementById('recipes');
    recipesDiv.innerHTML = '';
    data.forEach(recipe => {
        let recipeElement = document.createElement('div');
        recipeElement.innerHTML = `<h2>${recipe.title}</h2><img src="${recipe.image}" alt="${recipe.title}"><a href="${recipe.sourceUrl}">View Recipe</a>`;
        recipesDiv.appendChild(recipeElement);
    });
}