from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/download-links')
def download_links():
    base_url = 'https://vivaldi.com/zh-hans/download/'
    # 设置请求头部，模拟浏览器User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # 发送HTTP GET请求
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    download_links = []

    # 假设下载链接都在class为"download-link"的a标签中
    for link in soup.find_all('a', class_='download-link'):
        href = link.get('href')
        text = link.text.strip()
        os = link.get('data-os')
        cpu = link.get('data-cpu')

        download_links.append({
            'href': href,
            'text': text,
            'os': os,
            'cpu': cpu
        })

    return jsonify(download_links)

if __name__ == '__main__':
    app.run(debug=True)
