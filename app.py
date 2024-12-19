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
    text = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def user_exists(username):
    return User.query.filter_by(username=username).first() is not None

def save_user(username, hashed_password):
    new_user = User(username=username, password=hashed_password, streak=0, last_read_position=None)
    db.session.add(new_user)
    db.session.commit()

def get_user_data(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": "User not found"}
    bookmarks = [
        {
            "id": bookmark.id,
            "verse": bookmark.verse,
            "chapter": bookmark.chapter,
            "book": bookmark.book,
            "text": bookmark.text
        }
        for bookmark in user.bookmarks
    ]
    user_data = {
        "id": user.id,
        "username": user.username,
        "streak": user.streak,
        "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
        "last_read_position": user.last_read_position,
        "bookmarks": bookmarks
    }
    return user_data

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

@app.route('/add-bookmark', methods=['POST'])
def add_bookmark():
    data = request.json
    username = data.get('username')
    book = data.get('book')
    chapter = data.get('chapter')
    verse = data.get('verse')
    text = get_bible_section(book, chapter, verse)["text"]

    if not username or not book or not chapter or not verse:
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_bookmark = Bookmark(book=book, chapter=chapter, verse=verse, user_id=user.id, text=text)
    db.session.add(new_bookmark)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Bookmark added for {book} {chapter}:{verse} by {username}'}), 200


@app.route('/get-bookmarks', methods=['GET'])
def get_bookmarks():
    username = request.args.get('username')
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    bookmarks = [
        {
            "id": bookmark.id,
            "book": bookmark.book,
            "chapter": bookmark.chapter,
            "verse": bookmark.verse,
            'text': bookmark.text
        }
        for bookmark in user.bookmarks
    ]
    return jsonify(bookmarks)


#this needs a rework!!!!
@app.route('/delete-bookmark', methods=['DELETE'])
def delete_bookmark():
    # Get the parameters from the request
    data = request.get_json()
    username = data.get('username')
    book = data.get('book')
    chapter = data.get('chapter')
    verse = data.get('verse')

    # Ensure the user exists
    user = get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Find the bookmark in the user's bookmarks
    bookmark = next((b for b in user.bookmarks if b.book == book and b.chapter == chapter and b.verse == verse), None)

    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404

    # Delete the bookmark
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Bookmark deleted successfully'}), 200

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
    books = get_book_names_from_file()
    username = request.args.get('username')
    user = get_user_by_username(username)
    last_read_pos = user.last_read_position if user else None

    if request.method == 'POST':
        book = request.form.get('book')
        chapter = request.form.get('chapter')
        verse = request.form.get('verse')

        if user:
            user.last_read_position = f"{book} {chapter}:{verse}"
            db.session.commit()

    return render_template('bible_user.html', books=books, username=username, last_read_pos=last_read_pos)

@app.route('/user-text', methods=['GET'])
def bible_text_user():
    book = request.args.get('book')
    chapter = request.args.get('chapter', type=int)
    verse = request.args.get('verse', type=int)

    text = get_bible_section(book, chapter, verse)
    return jsonify({"text": text})


@app.route('/profile', methods=['GET', 'POST'])
def view_profile():
    username = request.args.get('username')
    user_data = get_user_data(username)
    return render_template('profile.html', user_data=user_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_exists(username) and validate_user_password(username, password):
            add_streak(username)
            return redirect(url_for('bible_user', username=username))
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
