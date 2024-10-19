from flask import Flask, request, jsonify
from models import db, User, FavoriteAnime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import pandas as pd
from Anime_weightedRec import recommend_anime, cosine_sim  # Import from Anime_weightedRec.py

# Initialize the Flask app
app = Flask(__name__)

# Configuration for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management

# Initialize the database with the Flask app
db.init_app(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not logged in

# Load the DataFrames
animes = pd.read_csv('AnimesCleaned.csv')  # For tags and cosine similarity
animes_updated = pd.read_csv('animes_updated.csv')  # For titles and UIDs

# ------------------- User Authentication ------------------- #

# Load the user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409  # Conflict

    # Create a new user
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'})

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'message': 'Login successful!'})
    return jsonify({'message': 'Invalid credentials'}), 401

# Route to logout
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'})

# ------------------- Recommendation System ------------------- #

# Route to get anime recommendations by UID using the imported function
@app.route('/recommend', methods=['GET'])
@login_required  # Protect this route so only logged-in users can access it
def recommend():
    uid = request.args.get('uid')  # Get the UID from the query parameter

    # Call the recommend_anime function imported from Anime_weightedRec.py
    recommended_animes = recommend_anime(int(uid), animes, cosine_sim)

    # Convert the DataFrame to a dictionary and pretty-print JSON
    recommended_animes_json = recommended_animes.to_dict(orient='records')

    # Return a pretty-printed JSON response
    return jsonify(recommended_animes_json)

# ------------------- Running the Flask App ------------------- #

if __name__ == '__main__':
    app.run(debug=True)
