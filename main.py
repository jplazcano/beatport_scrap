import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import streamlit as st

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def get_genre_links():
    """Fetch the genre links from the Beatport homepage."""
    url = 'https://www.beatport.com/'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find('div', {'class': 'genres-drop head-drop header-tooltip-menu'}).find_all('a')
    links = []
    for result in results:
        links.append(urljoin(url, f"{result['href']}/top-100"))
    return links

def extract_track_info(result):
    """Extract track information from a BeautifulSoup result object."""
    track_info = result.select('span.buk-track-primary-title, span.buk-track-remixed, p.buk-track-artists, p.buk-track-labels, p.buk-track-genre, p.buk-track-released')
    return [t.text.strip() for t in track_info]

def scrape_genre(url):
    """Scrape track information from a genre page."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.select('div.bucket.tracks ul li')
        return [extract_track_info(result) for result in results]
    except requests.exceptions.RequestException as e:
        print(f'Error scraping genre {url}: {e}')
        return []
@st.cache
def main():
    genre_links = get_genre_links()
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_genre, genre_links))
    data = [track for genre in results for track in genre]
    df = pd.DataFrame(data, columns=['Name', 'Remix', 'Artist', 'Label', 'Genre', 'Release Date'])
    return df

df = main()
st.dataframe(df)


