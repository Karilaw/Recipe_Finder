from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for
from flask_login import login_required, login_user, logout_user, LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import requests
from models import Recipe, db

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
    from models import User
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
            return redirect(url_for('find_recipes'))

    # Show the login form
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = generate_password_hash(password)

        # Check if a user with the given username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            flash('Username already taken. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # Create a new user and save it to the database
        user = User(username, password_hash)
        db.session.add(user)
        db.session.commit()

        # Flash a success message
        flash('You have successfully registered!', 'success')

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/find-recipes', methods=['GET', 'POST'])
def find_recipes():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        response = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey=240e492f44764327ac76abf321100d8b')
        if response.status_code == 200:
            flash('Request submitted successfully!', 'success')
            recipes = response.json()
            recipe = Recipe(data=recipes)  # Create a new Recipe object
            db.session.add(recipe)  # Add the new Recipe to the session
            db.session.commit()  # Commit the session to save the Recipe
            return redirect(url_for('recipe_list'))  # Redirect to the recipe_list route
        else:
            flash('There was an error submitting the request.', 'error')
    return render_template('find_recipes.html')

@app.route('/recipe-details/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_details(recipe_id):
    apiKey = 'YOUR_API_KEY'  # Replace with your actual API key
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey=240e492f44764327ac76abf321100d8b'
    response = requests.get(url)
    recipe = response.json()
    return render_template('recipe_details.html', recipe=recipe)

@app.route('/recipe-list', methods=['GET', 'POST'])
def recipe_list():
    # Get the recipes from the database
    recipe_objects = Recipe.query.all()
    recipes = [recipe.data for recipe in recipe_objects]  # Extract the recipe dictionaries
    return render_template('recipe_list.html', recipes=recipes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)