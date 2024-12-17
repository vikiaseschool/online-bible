from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import get_verse_for_today, get_bible_section, get_book_names_from_file
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    streak = db.Column(db.Integer, default=1)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_position = db.Column(db.String(100))
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    verse = db.Column(db.String(150), nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    book = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def user_exists(username):
    return User.query.filter_by(username=username).first() is not None

def save_user(username, hashed_password):
    new_user = User(username=username, password=hashed_password, streak=0, last_read_position=None)
    db.session.add(new_user)
    db.session.commit()

def validate_user_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return True
    else:
        return False

def add_streak(username):
    user = User.query.filter_by(username=username).first()
    if user:
        current_date = datetime.now().date()
        last_login_date = user.last_login.date()
        if current_date == last_login_date + timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
        user.last_login = datetime.now()
        db.session.commit()
        return user.streak
    else:
        return None



@app.route('/')
def index():
    verse = get_verse_for_today()
    return render_template('index.html', verse=verse)

@app.route('/guest')
def bible_guest():
    books = get_book_names_from_file()
    return render_template('bible_guest.html', books=books)

@app.route('/bible-text', methods=['GET'])
def bible_text_guest():
    book = request.args.get('book')
    chapter = request.args.get('chapter', type=int)
    verse = request.args.get('verse', type=int)

    text = get_bible_section(book, chapter, verse)
    return jsonify({"text": text})

@app.route('/user')
def bible_user():
    return render_template('bible_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_exists(username) and validate_user_password(username, password):
            add_streak(username)
            return redirect(url_for('bible_user'))
        else:
            return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html', error=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form.get('new-username')
        new_password = request.form['new-password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        if user_exists(new_username):
            return render_template('login.html', error="Username already exists.")

        save_user(new_username, hashed_password)
        return redirect(url_for('login'))

    return render_template('login.html', error=None)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
