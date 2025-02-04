from bs4 import BeautifulSoup
import requests

def imageSearch(image_url: str):
    output = []
    session = requests.Session()
    session.headers.update({'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'})
    upload_response = session.get('https://lens.google.com/uploadbyurl', params={'url': image_url.replace("preview", "i", 1)}, timeout=5)
    soup = BeautifulSoup(upload_response.text, features="html.parser")
    exact = next((str(links.get('href')) for links in soup.find_all('a') if 'udm=48' in str(links.get('href'))), '')
    response = session.get(upload_response.url + exact, timeout=5)
    soup2 = BeautifulSoup(response.text, features="html.parser")
    output = [str(links.get('href')) for links in soup2.find_all('a') if links.get('href') and '/search?' not in links.get('href') and 'google.com/' not in links.get('href')]
    return output

def sortMedia(gallery_data):
    ordered_ids = sorted(item['id'] for item in gallery_data['items'])
    media_ids = [j['media_id'] for i in ordered_ids for j in gallery_data['items'] if i == j['id']]
    return media_ids