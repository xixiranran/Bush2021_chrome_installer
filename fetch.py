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
                    
        # 初始化综合信息列表
        combined_info = []
    
        # 寻找所有包含版本信息和下载链接的.list div
        for list_div in soup.find_all('div', class_='list'):
            # 寻找每个.list div中的<p>标签以获取版本信息
            p_tag = list_div.find('p', id=None)
            if p_tag:
                # 分割文本获取版本号和更新时间
                parts = p_tag.text.split()
                if len(parts) >= 3:  # 确保有足够的文本部分
                    version = parts[0]  # 第一个部分是版本号
                    date = parts[-1].strip('[]')  # 最后一个部分是日期，去除方括号
    
                    # 寻找下载链接
                    for button_div in list_div.find_all('div', class_='button'):
                        for link in button_div.find_all('a', href=True):
                            if "便携版" in link.text:
                                full_url = requests.utils.urljoin(url, link['href'])
                                combined_info.append({
                                    'version': version,
                                    'date': date,
                                    'download_links': [{'href': full_url, 'text': link.text.strip()}]
                                })
    
        # 打印综合信息
        for info in combined_info:
            print(f"Version: {info['version']}, Date: {info['date']}, Download Link: {info['download_links'][0]['href']}")
    
        # 将综合信息保存到JSON文件中
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(combined_info, f, ensure_ascii=False, indent=4)
        
        print("Portable download links have been updated.")
        break
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        continue
