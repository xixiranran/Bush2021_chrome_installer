import requests
from bs4 import BeautifulSoup

# 目标网页的URL
url = 'https://vivaldi.com/zh-hans/download/'

# 发送HTTP GET请求
response = requests.get(url)

# 确保请求成功
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到所有的下载链接
    # 注意：选择器需要根据实际网页的结构来确定
    # 假设所有的下载链接都在class为"download-link"的a标签中
    download_links = soup.find_all('a', class_='download-link')
    
    # 遍历所有找到的链接并打印
    for link in download_links:
        # 获取链接的href属性，即下载的URL
        download_url = link.get('href')
        print(f'下载链接: {download_url}')
else:
    print('请求页面失败，状态码：', response.status_code)
