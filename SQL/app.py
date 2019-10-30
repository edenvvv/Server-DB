from flask import Flask, request, abort, g
import uuid
import sqlite3

DATABASE = './database.db'


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_or_update_db(query, args=()):
    db = get_db()
    db.cursor().execute(query, args)
    db.commit()


def verify_token(token):
    if len(token) != 36:
        abort(400, 'The token must contain 36 characters')  # 400 Bad Request

    user_object = query_db('SELECT * FROM users WHERE token=?', (token,), one=True)
    # Searching for the token (Get token back)
    if user_object is None:
        abort(404, 'token not found')  # 404 not found
    return user_object


def check_username(name):
    if query_db('SELECT count(*) FROM users WHERE username=?', (name,), one=True)[0] == 1:
        # Check if the username already exists
        abort(400, 'The username already exists')  # 400 Bad Request


def validate_username(name):
    char = any((((char >= 'a') and (char <= 'z')) or ((char >= 'A') and (char <= 'Z'))) for char in name)
    # Checks if there is at least one letter
    if char is False:
        abort(400, 'There must be a letter')  # 400 Bad Request


def validate_password(password):
    if len(password) < 8:
        # Checks if the password is more than 8 digits
        abort(400, 'String must be at least 8 characters long')  # 400 Bad Request

    low = any(((char >= 'a') and (char <= 'z')) for char in password)
    # Checks if there is at least one lowercase letter
    up = any(((char >= 'A') and (char <= 'Z')) for char in password)
    # Checks if there is at least one uppercase letter
    if low is False and up is False:
        abort(400, 'There must be a lowercase and uppercase letter')  # 400 Bad Request
    elif low is False:
        abort(400, 'There must be a lowercase letter')  # 400 Bad Request
    elif up is False:
        abort(400, 'There must be a uppercase letter')  # 400 Bad Request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Just a regular key for now'


@app.route('/register', methods=['POST'])  # allow POST requests
def register():
    with app.app_context():
        json_data = request.get_json()
        username = json_data['name']
        password = json_data['password']
        validate_username(username)
        # Checking username valid
        validate_password(password)
        # Checking password valid
        check_username(username)
        # Check if the username already exists

        insert_or_update_db('INSERT INTO users VALUES (?,?,?)', (username, password, None))
        return 'registration succeeded!'


@app.route('/login', methods=['POST'])  # allow POST requests
def login():
    with app.app_context():
        json_data = request.get_json()
        username = json_data['name']
        password = json_data['password']
        validate_username(username)
        # Checking username valid
        validate_password(password)
        # Checking password valid

        user_object = query_db('SELECT * FROM users WHERE username=?', (username,), one=True)
        # Searching for the username (Get user back)
        if user_object is None:
            # Checks if the user name exists
            abort(404, 'user could not be found')  # 404 not found
        if user_object[1] != password:
            # Checks if the password is incorrect
            abort(400, 'There is probably a password typing error')  # 400 Bad Request
        # Creates token
        token = str(uuid.uuid4())
        insert_or_update_db("UPDATE users SET token = (?) WHERE username = (?) ", (token, username))
        return f"Your token is: {token}"


@app.route('/chat', methods=['POST'])  # allow POST requests
def chat():
    json_data = request.get_json()
    user = verify_token(json_data['token'])
    # Checks token
    text = json_data['text']
    print("{}: {}".format(user[0], text))
    return 'OK'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#  Take care of updating the server
if __name__ == '__main__':
    app.run(debug=True)
