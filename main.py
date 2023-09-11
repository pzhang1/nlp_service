from typing import List

from bs4 import BeautifulSoup
from fastapi import FastAPI
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string, STOPWORDS
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from gensim.parsing.preprocessing import strip_punctuation
from gensim.parsing.preprocessing import strip_non_alphanum
from gensim.parsing.preprocessing import split_alphanum
from gensim.parsing.preprocessing import strip_numeric
from gensim.parsing.preprocessing import remove_stopwords
from typing import List, Dict, Any
import sqlite3
from pydantic import BaseModel

# Create a new FastAPI app
app = FastAPI(
    title="Theme Extraction Web Service",
    description="A FastAPI based web service that performs theme extraction for web pages and "
                "persists the data in an SQLite database.",
    version="1.0.0",
)

# Define the database schema
Base = declarative_base()


class Theme(Base):
    __tablename__ = 'themes'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    theme = Column(String, index=True)
    relevance = Column(Float, index=True)

class URL(BaseModel):
    url: str

def create_themes_table():
    conn = sqlite3.connect('themes.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS themes
                (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, theme TEXT, relevance REAL)''')

    conn.commit()
    conn.close()


create_themes_table()

# Define the SQLAlchemy engine and session
engine = create_engine('sqlite:///themes.db')
Session = sessionmaker(bind=engine)
session = Session()

# Define Gensim dictionary, model, and stop words
dictionary = Dictionary.load('model/dictionary.gensim')
model = LdaModel.load('model/lda_model.gensim')
stopwords = STOPWORDS.union(set(['href', 'www', 'com', 'html']))


def extract_themes(text: str) -> List[str]:
    # Tokenize, preprocess, and convert text to bag-of-words
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_punctuation, strip_non_alphanum, split_alphanum, strip_numeric,
                      remove_stopwords]
    print("[LOG]: Extracting in process")
    tokens = preprocess_string(text.lower(), filters=CUSTOM_FILTERS)
    # tokens = preprocess_string(text.lower(), filters=[lambda x: x.lower() in stopwords])
    bow = dictionary.doc2bow(tokens)

    # Extract themes from the bag-of-words using the LDA model
    theme_tuples = model.get_document_topics(bow)
    # print(theme_tuple)
    theme_ids = [theme_tuple[0] for theme_tuple in theme_tuples]
    themes = [model.show_topic(theme_id)[0][0] for theme_id in theme_ids]
    print("[LOG]: themes extracted:")
    print(themes)
    return themes


@app.post('/themes')
async def add_themes(url: URL):
    response = requests.get(url.url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    themes = extract_themes(text)

    for theme in themes:
        relevance = themes.count(theme) / len(themes)
        themerow = Theme(url=url.url, theme=theme, relevance=relevance)
        session.add(themerow)

    session.commit()
    return {"message": f"Extracted {len(themes)} themes from {url}."}

@app.get("/themes/extracted")
def extracted_themes() -> List[str]:
    conn = sqlite3.connect('themes.db')
    c = conn.cursor()

    # Select the distinct themes in the table
    c.execute("SELECT DISTINCT theme FROM themes")
    themes = [row for row in c.fetchall()]

    conn.close()

    # Combine the themes from each row into one list
    extracted_themes = list(set([theme for row in themes for theme in row]))

    return extracted_themes

@app.get("/themes/detected")
def detected_themes() -> Dict[str, List[str]]:
    conn = sqlite3.connect('themes.db')
    c = conn.cursor()

    # Select the texts in the table along with their detected themes
    c.execute("SELECT url, theme, relevance FROM themes")
    rows = [row for row in c.fetchall()]

    conn.close()
    # print("[LOG]: ")
    # print(rows[0])
    # print(rows[1])

    # Combine the detected themes from each row into one list
    detected_themes = list(set([row[1] for row in rows]))
    # print("[LOG]:")
    # print(detected_themes)
    # Create a dictionary mapping each detected theme to a list of texts that contain it
    texts_with_themes = {}
    for theme in detected_themes:
        texts_with_themes[theme] = [row[0] for row in rows if theme in row[1]]

    return texts_with_themes

