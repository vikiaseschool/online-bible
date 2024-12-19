import random
import json


#vraci dict: {"text": "text", "reference": "reference"}
def get_verse_for_today():
    key_books_with_chapters = {
        "Genesis": 50,
        "Exodus": 40,
        "Psalms": 150,
        "Isaiah": 66,
        "Matthew": 28,
        "John": 21,
        "Acts": 28,
        "Romans": 16,
        "Revelation": 22
    }

    verses = []
    bible = load_bible()

    for book, max_chapter in key_books_with_chapters.items():
        chapter = random.randint(1, max_chapter)  # Select a random chapter
        book_data = next((item for item in bible['books'] if item['name'] == book), None)

        if book_data:
            chapter_data = next((item for item in book_data['chapters'] if item['chapter'] == chapter), None)
            if chapter_data:
                max_verse = len(chapter_data['verses'])  # Get the number of verses in the selected chapter
                verse_number = random.randint(1, max_verse)  # Select a random verse number
                verse_data = chapter_data['verses'][verse_number - 1]  # Index is zero-based

                verses.append({
                    "text": verse_data.get("text", "Verse not found"),
                    "reference": f"{book} {chapter}:{verse_number}"
                })
    verse_today = random.choice(verses) if verses else None
    verse_today["text"] = verse_today["text"].replace(";", "").replace("’", "").replace("‘", "").replace(
        "”", "").replace("“", "").replace("⌞", "").replace("⌜", "").replace("⌟",
                                                                            "").replace(
        "⌝", "").replace("—", "")
    return verse_today

def load_bible():
    with open('/home/vikiase/online-bible/full_bible.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def clean_text(data):
    for chapter in data.get("chapters", []):
        for verse in chapter.get("verses", []):
            verse["text"] = verse["text"].replace(";", "")
            verse["text"] = verse["text"].replace("’", "")
            verse["text"] = verse["text"].replace("‘", "")
            verse["text"] = verse["text"].replace("”", "")
            verse["text"] = verse["text"].replace("“", "")
            verse["text"] = verse["text"].replace("⌞", "")
            verse["text"] = verse["text"].replace("⌜", "")
            verse["text"] = verse["text"].replace("⌟", "")
            verse["text"] = verse["text"].replace("⌝", "")
            verse["text"] = verse["text"].replace("—", "")
    return data
def get_bible_section(book, chapter=None, verse=None):
    bible_data = load_bible()

    for bible_book in bible_data['books']:
        if bible_book['name'].lower() == book.lower():
            if chapter is None:
                return clean_text(bible_book)
            else:
                for ch in bible_book['chapters']:
                    if ch['chapter'] == chapter:
                        if verse is None:
                            return clean_text({'chapters': [ch]})
                        else:
                            for v in ch['verses']:
                                if v['verse'] == verse:
                                    v["text"] = v["text"].replace(";", "").replace("’", "").replace("‘", "").replace(
                                        "”", "").replace("“", "").replace("⌞", "").replace("⌜", "").replace("⌟",
                                                                                                            "").replace(
                                        "⌝", "").replace("—", "")

                                    return v
    return 'Not Found.'

def get_book_names_from_file():
    with open('/home/vikiase/online-bible/full_bible.json', 'r', encoding='utf-8') as f:
        bible_data = json.load(f)
    book_names = [book['name'] for book in bible_data['books']]
    custom_order = [
        'Genesis', 'Exodus', 'Psalms', 'Isaiah', 'Deuteronomy',
        'Matthew', 'John', 'Acts', 'Romans', 'Revelation of John'
    ]
    first_ten = [book for book in custom_order if book in book_names]
    remaining_books = [book for book in book_names if book not in first_ten]
    reordered_books = first_ten + remaining_books
    return reordered_books



