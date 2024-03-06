from flask import Flask, flash, redirect, render_template, request, jsonify, url_for
from flask_login import login_required, login_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash
import requests
from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a\xe0\xf9\x0fxkhX5e\tQ\xdd\x05\xc8\xe2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager()

login_manager.init_app(app)

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
def get_recipes():
    ingredients = request.json['ingredients']
    response = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey=240e492f44764327ac76abf321100d8b')
    return jsonify(response.json())

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
@login_required
def find_recipes():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        # Your code to find recipes
    return render_template('find_recipes.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)