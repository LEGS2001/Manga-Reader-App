from flask import Flask, render_template, request
import requests
import json
import ast
import os

def get_mangas(title):
    url = f'https://api.mangadex.org/manga?title={title}'
    response = requests.get(url)
    return response.json()['data']

def get_chapters(manga_id):
    url = f'https://api.mangadex.org/manga/{manga_id}/feed?translatedLanguage[]=en'
    response = requests.get(url)
    return response.json()['data']

def get_pages(chapter_id):
    url = f'https://api.mangadex.org/at-home/server/{chapter_id}'
    response = requests.get(url)

    base_url = response.json()['baseUrl']
    chapter_hash = response.json()['chapter']['hash']
    pages = response.json()['chapter']['data']

    image_urls = [f'{base_url}/data/{chapter_hash}/{page}' for page in pages]
    return image_urls

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_manga', methods=['GET', 'POST'])
def find_manga():
    manga_name = request.form['manga_name']
    mangas = get_mangas(manga_name)

    if not mangas:
        # TODO: HACER UN HTML QUE PERMITA VOLVER AL INDEX
        return 'No mangas'
    
    return render_template('select_manga.html', mangas=mangas)

@app.route('/select_chapter', methods=['GET', 'POST'])
def select_chapter():
    manga = request.form.get('manga')

    # convierte los single quotes ' en double quotes " para que el JSON sea válido
    manga = json.dumps(ast.literal_eval(manga))
    manga = json.loads(manga)

    manga_id = manga['id']
    chapters = get_chapters(manga_id)
    if not chapters:
        # TODO: HACER UN HTML QUE PERMITA VOLVER AL INDEX
        return 'No chapters found'
    
    chapters = sorted(chapters, key=lambda x: float(x['attributes']['chapter']))
    return render_template('select_chapter.html', chapters=chapters)

@app.route('/read_chapter', methods=['GET', 'POST'])
def read_chapter():
    chapter_id = request.form.get('chapter_id')
    pages = get_pages(chapter_id)
    return render_template('read_chapter.html', pages=pages)

if __name__ == '__main__':
    app.run(debug=True)