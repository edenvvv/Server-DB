from flask import Flask, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
import uuid


def verify_token(token):
    if len(token) != 36:
        abort(Response('The token must contain 36 characters'), 400)  # 400 Bad Request

    user_object = User.query.filter_by(token=token).first()
    # Searching for the token
    if user_object is None:
        abort(Response('token not found'), 404)  # 404 not found
    return user_object


def check_username(name):
    user_object = User.query.filter_by(username=name).first()
    if user_object is not None:
        # Check if the username already exists
        abort(Response('The username already exists'), 400)  # 400 Bad Request


def validate_username(name):
    char = any((((char >= 'a') and (char <= 'z')) or ((char >= 'A') and (char <= 'Z'))) for char in name)
    # Checks if there is at least one letter
    if char is False:
        abort(Response('There must be a letter'), 400)  # 400 Bad Request


def validate_password(password):
    if len(password) < 8:
        # Checks if the password is more than 8 digits
        abort(Response('String must be at least 8 characters long'), 400)  # 400 Bad Request

    low = any(((char >= 'a') and (char <= 'z')) for char in password)
    # Checks if there is at least one lowercase letter
    up = any(((char >= 'A') and (char <= 'Z')) for char in password)
    # Checks if there is at least one uppercase letter
    if low is False and up is False:
        abort(Response('There must be a lowercase and uppercase letter'), 400)  # 400 Bad Request
    elif low is False:
        abort(Response('There must be a lowercase letter'), 400)  # 400 Bad Request
    elif up is False:
        abort(Response('There must be a uppercase letter'), 400)  # 400 Bad Request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Just a regular key for now'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Top\\Desktop\\flask\\DB.db'
db = SQLAlchemy(app)


class User(db.Model):
    # get data
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/register', methods=['POST'])  # allow POST requests
def register():
    json_data = request.get_json()
    username = json_data['name']
    password = json_data['password']
    validate_username(username)
    # Checking username valid
    validate_password(password)
    # Checking password valid
    check_username(username)
    # Check if the username already exists
    user = User(username, password)
    db.session.add(user)
    # add to DB
    db.session.commit()
    return 'registration succeeded!'


@app.route('/login', methods=['POST'])  # allow POST requests
def login():

    json_data = request.get_json()
    username = json_data['name']
    password = json_data['password']
    validate_username(username)
    # Checking username valid
    validate_password(password)
    # Checking password valid

    user_object = User.query.filter_by(username=username).first()
    # Searching for the username (Get user back)
    if user_object is None:
        # Checks if the user name exists
        abort(Response('user could not be found'), 404)  # 404 not found
    if user_object.password != password:
        # Checks if the password is incorrect
        abort(Response('There is probably a password typing error'), 400)  # 400 Bad Request
    # Creates token
    user_object.token = str(uuid.uuid4())
    db.session.add(user_object)
    db.session.commit()
    return user_object.token


@app.route('/chat', methods=['POST'])  # allow POST requests
def chat():
    json_data = request.get_json()
    user = verify_token(json_data['token'])
    # Checks token
    text = json_data['text']
    print("{}: {}".format(user['token'], text))
    return 'OK'


#  Take care of updating the server
if __name__ == '__main__':
    app.run(debug=True)
