import json
from flask import Flask, abort, flash, redirect, render_template, request, jsonify, session, url_for
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import requests
from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a\xe0\xf9\x0fxkhX5e\tQ\xdd\x05\xc8\xe2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager()

login_manager.init_app(app)

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)

with app.app_context():
    from models import User, Recipe, Contact
    db.create_all()

from models import get_user_from_database
from models import save_user_to_database


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/recipes', methods=['POST'])
def get_recipes(ingredients):
    response = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey=240e492f44764327ac76abf321100d8b')
    return response.json()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user is not None and user.check_password(password):
            # Log the user in and redirect to the find_recipes route
            login_user(user)
            flash('Login successful!', 'success')  # Display a success message
            return redirect(url_for('find_recipes'))
        else:
            flash('Invalid username or password.', 'error')  # Display an error message

    # Show the login form
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        # Check if the username and password meet the preferred standard
        if len(username) < 5 or len(password) < 8:
            flash('Username must be at least 5 characters and password must be at least 8 characters.', 'error')
            return redirect(url_for('register'))

        # Check if a user with the given username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user is not None:
            flash('Username or email already taken. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)  # replace 'password' with 'password_hash'

        # Save the new user to the database
        db.session.add(user)
        db.session.commit()

        # Flash a success message
        flash('You have successfully registered!', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/find-recipes', methods=['GET', 'POST'])
@login_required  # ensure the user is logged in
def find_recipes():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        response = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey=240e492f44764327ac76abf321100d8b')
        if response.status_code == 200:
            recipes = response.json()
            if recipes:  # check if the response contains data
                print(recipes)
                for recipe_data in recipes:
                    # Check if a Recipe with this spoonacular_id already exists
                    existing_recipe = Recipe.query.get(recipe_data['id'])
                    if existing_recipe is None:
                        # If not, create a new Recipe
                        recipe = Recipe(spoonacular_id=recipe_data['id'], data=recipe_data, user_id=current_user.id)  # associate each recipe with the current user
                        db.session.add(recipe)
                db.session.commit()
                flash('Request submitted successfully!', 'success')  # flash the success message
                return redirect(url_for('recipe_list'))  # redirect to the recipe_list page
            else:
                flash('There was an error submitting the request. No data was returned.', 'error')
        else:
            flash('There was an error submitting the request.', 'error')
    return render_template('find_recipes.html')

@app.route('/recipe-details/<int:spoonacular_id>', methods=['GET', 'POST'])
def recipe_details(spoonacular_id):
    apiKey = 'YOUR_API_KEY'  # Replace with your actual API key
    url = f'https://api.spoonacular.com/recipes/{spoonacular_id}/information?apiKey=240e492f44764327ac76abf321100d8b'
    response = requests.get(url)
    recipe = response.json()
    return render_template('recipe_details.html', recipe=recipe)


@app.route('/recipe-list', methods=['GET', 'POST'])
@login_required  # ensure the user is logged in
def recipe_list():
    # Get the recipes from the database for the current user, ordered by the time they were added (most recent first)
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.timestamp.desc()).all()
    return render_template('recipe_list.html', recipes=recipes)

@app.route('/delete-recipe/<int:spoonacular_id>', methods=['POST'])
@login_required
def delete_recipe(spoonacular_id):
    # Get the Recipe instance from the database using the spoonacular_id
    recipe = Recipe.query.get(spoonacular_id)
    if recipe:
        # Check if the user is authorized to delete the recipe
        if recipe.user_id != current_user.id:
            flash("You do not have permission to delete this recipe.", "error")
            return redirect(url_for("recipe_list"))
        # Delete the recipe
        db.session.delete(recipe)
        db.session.commit()
        flash('Your recipe has been deleted!', 'success')
        return redirect(url_for('recipe_list'))
    # If no recipe with the given spoonacular_id is found
    flash('The recipe you are trying to delete does not exist.', 'error')
    return redirect(url_for('recipe_list'))

@app.route('/add-to-favorites/<int:spoonacular_id>', methods=['POST'])
@login_required
def add_to_favorites(spoonacular_id):
    recipe = Recipe.query.filter_by(spoonacular_id=spoonacular_id, user_id=current_user.id).first()
    if recipe:
        recipe.is_favorite = True
        db.session.commit()
        flash('Recipe added to favorites!', 'success')
    else:
        flash('Recipe not found.', 'error')
    return redirect(url_for('recipe_list'))

@app.route('/favorite-recipes', methods=['GET'])
@login_required
def favorite_recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id, is_favorite=True).all()
    return render_template('favorite_recipes.html', recipes=recipes)

@app.route('/remove-from-favorites/<int:spoonacular_id>', methods=['POST'])
@login_required
def remove_from_favorites(spoonacular_id):
    recipe = Recipe.query.filter_by(spoonacular_id=spoonacular_id, user_id=current_user.id).first()
    if recipe:
        recipe.is_favorite = False  # Mark the recipe as not favorite
        db.session.commit()
        flash('Recipe removed from favorites!', 'success')
    else:
        flash('Recipe not found.', 'error')
    return redirect(url_for('favorite_recipes'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.template_filter('to_int')
def to_int(value):
    return int(value)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create a new Contact object
        contact = Contact(name=name, email=email, message=message)

        # Add the new Contact object to the database
        db.session.add(contact)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    else:
        return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)