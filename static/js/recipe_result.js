// Function to fetch recipes based on ingredients
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

// Function to display fetched recipes
function displayRecipes(data) {
    let recipesDiv = document.getElementById('recipes');
    recipesDiv.innerHTML = '';
    data.forEach(recipe => {
        let recipeElement = document.createElement('div');
        recipeElement.innerHTML = `<h2>${recipe.title}</h2><img src="${recipe.image}" alt="${recipe.title}"><a href="${recipe.sourceUrl}">View Recipe</a>`;
        recipesDiv.appendChild(recipeElement);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Event listener for submit-button
    let submitButton = document.getElementById('submit-button');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            this.style.fontWeight = 'bold';
        });
    }

    // // jQuery code for navigation
    // $("nav a").click(function(event){
    //     event.preventDefault();
    //     var href = this.getAttribute('href');
    //     var targetElement = document.querySelector(`a[href='${href}']`);
    //     if (targetElement) {
    //         smoothScroll(targetElement, 1000);
    //     }
    // });

    // Show footer when user scrolls to bottom of the page
    // window.addEventListener('scroll', function() {
    //     var footer = document.querySelector('footer');
    //     var scrollPosition = window.innerHeight + window.scrollY;

    //     if (scrollPosition >= document.body.offsetHeight) {
    //         footer.style.display = 'block';
    //     } else {
    //         footer.style.display = 'none';
    //     }
    // });
});