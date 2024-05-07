import requests
from bs4 import BeautifulSoup
import json

# 目标网页的URL
url = 'https://vivaldi.com/zh-hans/download/'

# 设置请求头部，模拟浏览器User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 发送HTTP GET请求
response = requests.get(url, headers=headers)

# 确保请求成功
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到所有的exe和apk下载链接
    download_links = []

    # 寻找exe下载链接，假设它们在class为"download-link"的a标签中
    for i, link in enumerate(soup.find_all('a', class_='download-link')):
        if i == 0:  # 忽略第一个链接
            continue
        href = link.get('href')
        text = link.text.strip()
        download_links.append({'href': href, 'text': text})
    
    # 寻找apk下载链接，假设它们在id为"dl-mobile"的div中的a标签下
    apk_parent_div = soup.find('div', id='dl-mobile')
    if apk_parent_div:
        for apk_link in apk_parent_div.find_all('a', href=True):
            if apk_link['href'].endswith('.apk'):
                download_links.append({'href': apk_link['href'], 'text': apk_link.text.strip()})

    # 将下载链接保存到一个JSON文件中
    with open('data.json', 'w') as f:
        json.dump(download_links, f, indent=4)
    
    print("Download links have been updated.")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
