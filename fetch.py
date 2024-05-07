import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# 目标网页的URL
url = 'https://www.centbrowser.cn/history.html'

# 设置请求头部，模拟浏览器User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
while True:
    # 发送HTTP GET请求
    response = requests.get(url, headers=headers)
    # print("response.text:",response.text)
    # print("response.status_code:",response.status_code)
    # 确保请求成功
    if response.status_code == 200:
        # 尝试将响应内容解码为utf-8，如果失败则使用默认编码
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        download_links = []
    
        # 寻找exe下载链接，假设它们在class为"button"的a标签中
        # 由于您只想要便携版的链接，这里我们可以根据文本内容来过滤
        # 寻找包含“便携版”文本的下载链接
        for button_div in soup.find_all('div', class_='button'):
            for link in button_div.find_all('a', href=True):
                if "便携" in link.text:
                    full_url = urljoin(url, link['href'])
                    # print("full_url:",full_url)
                    download_links.append({'href': full_url, 'text': link.text.strip()})
    
        # 将下载链接保存到一个JSON文件中
        with open('data.json', 'w') as f:
            json.dump(download_links, f, indent=4)
        
        print("Portable download links have been updated.")
        break
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        continue
