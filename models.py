import requests
import random
import json

#vraci dict: {"text": "text", "reference": "reference"}
def get_verse_for_today():
    def get_random_verse_from_key_books():
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

        for book, max_chapter in key_books_with_chapters.items():
            chapter = random.randint(1, max_chapter)
            verse = random.randint(1, 50)

            url = f"https://bible-api.com/{book} {chapter}:{verse}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                verses.append({
                    "text": data.get("text", "Verse not found"),
                    "reference": data.get("reference", f"{book} {chapter}:{verse}")
                })
            else:
                continue
        return random.choice(verses)

    verse_of_the_day = get_random_verse_from_key_books()

    if verse_of_the_day:
        verse_of_the_day['text'] = verse_of_the_day['text'][:-2]
        return verse_of_the_day
    else:
        print("Failed to retrieve the verse of the day.")

def load_bible():
    with open('full_bible.json', 'r', encoding='utf-8') as file:
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
    with open('full_bible.json', 'r', encoding='utf-8') as f:
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

