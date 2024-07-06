import time
import re
import requests
import MeCab
import ipadic
from tqdm import tqdm
from wordcloud import WordCloud
from bs4 import BeautifulSoup

mecab = MeCab.Tagger(f"{ipadic.MECAB_ARGS} -Ochasen")
mecab.parse("")

stop_words = [
    "そう",
    "ない",
    "いる",
    "する",
    "まま",
    "よう",
    "てる",
    "なる",
    "こと",
    "もう",
    "いい",
    "ある",
    "ゆく",
    "れる",
    "なっ",
    "ちゃっ",
    "ちょっ",
    "ちょっ",
    "やっ",
    "あっ",
    "ちゃう",
    "その",
    "あの",
    "この",
    "どの",
    "それ",
    "あれ",
    "これ",
    "どれ",
    "から",
    "なら",
    "だけ",
    "じゃあ",
    "られ",
    "たら",
    "のに",
    "って",
    "られ",
    "ずっ",
    "じゃ",
    "ちゃ",
    "くれ",
    "なんて",
    "だろ",
    "でしょ",
    "せる",
    "なれ",
    "どう",
    "たい",
    "けど",
    "でも",
    "って",
    "まで",
    "なく",
    "もの",
    "ここ",
    "どこ",
    "そこ",
    "さえ",
    "なく",
    "たり",
    "なり",
    "だっ",
    "まで",
    "ため",
    "なん",
    "ながら",
    "より",
    "られる",
    "です",
    "ただ",
    "みたい",
    "いく"
]


def getArtistIdByArtistName(artistName: str):
    url = f"https://www.uta-net.com/search/?target=art&type=in&Keyword={artistName}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    artist_list = soup.find(class_="songlist-table-block")
    artist = artist_list.find_all(href=re.compile("/artist/"))
    if artist:
        return artist[0].get("href").split("/")[-2]
    else:
        return None


def getSongsByArtistId(artistId: int):
    url = f"https://www.uta-net.com/artist/{artistId}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    song_list = soup.find(class_="songlist-table")
    songs = song_list.find_all(href=re.compile("/song/"))
    if songs:
        return [song.get("href").split("/")[-2] for song in songs]
    else:
        return None


def getLyricsBySongId(songId: int):
    url = f"https://www.uta-net.com/song/{songId}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics = soup.find_all("div", id="kashi_area")
    if lyrics:
        return lyrics[0].get_text("\n", strip=True).replace("　", " ")
    else:
        return None


def wakati_text(text):
    node = mecab.parseToNode(text)
    terms = []
    while node:
        term = node.surface
        pos = node.feature.split(",")[0]
        if pos in ["動詞", "形容詞", "名詞"]:
            if len(term) > 1:
                terms.append(term)
        node = node.next
    return terms


def generate(lyrics_list: list[str]):
    words = "".join(
        [" ".join(list(set(wakati_text(lyrics)))) for lyrics in lyrics_list]
    )
    wordcloud = WordCloud(
        font_path="./NotoSansJP-Regular.ttf",
        width=1280,
        height=720,
        background_color="white",
        collocations=False,
        stopwords=stop_words,
    ).generate(words)
    wordcloud.to_file("./wordcloud.png")


def main():
    lyrics_list = []
    artist_name = input("artist_name: ")
    artist_id = getArtistIdByArtistName(artist_name)
    print(f"artist_id: {artist_id}")
    song_ids = getSongsByArtistId(artist_id)
    print(song_ids)
    for song_id in tqdm(song_ids):
        lyrics = getLyricsBySongId(song_id)
        alphabet_removed_lyrics = re.sub(r"[a-zA-Z]", "", lyrics)
        lyrics_list.append(alphabet_removed_lyrics)
        time.sleep(1)
    generate(lyrics_list)


if __name__ == "__main__":
    main()
