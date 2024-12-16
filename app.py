from flask import Flask, render_template, request, jsonify
from models import get_verse_for_today, get_bible_section, get_book_names_from_file

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
