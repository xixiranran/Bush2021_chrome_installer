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
                    
        # 找到所有的版本信息
        version_info = []
    
        # 寻找所有包含版本信息的.list div
        for list_div in soup.find_all('div', class_='list'):
            # 寻找每个.list div中的<p>标签
            p_tag = list_div.find('p', id=None)  # id=None 确保选择的是不带id的<p>标签
            if p_tag:
                # 分割文本获取版本号和更新时间
                text_parts = p_tag.text.split()
                if len(text_parts) >= 2:  # 确保有足够的文本部分
                    version = text_parts[0]  # 第一个部分是版本号
                    date = text_parts[-1]  # 最后一个部分是日期
                    # 检查日期格式是否正确
                    if date.startswith('[') and date.endswith(']'):
                        date = date[1:-1]  # 移除日期的括号
                        version_info.append({'version': version, 'date': date})
    
        # 打印版本信息
        for info in version_info:
            print(f"Version: {info['version']}, Date: {info['date']}")

    
        # 如果需要，也可以将版本信息保存到JSON文件中
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=4)
        # 将下载链接保存到一个JSON文件中
        # with open('data.json', 'w') as f:
        #     json.dump(download_links, f, indent=4)
        
        print("Portable download links have been updated.")
        break
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        continue
