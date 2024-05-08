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
            version_info = list_div.find('p')  # 寻找<p>标签以获取版本信息
            print("version_info:",version_info)
            if version_info:
                # 拆分文本获取版本号和更新时间
                version_parts = version_info.text.split()
                if len(version_parts) > 1:  # 确保有足够的文本部分
                    version = version_parts[0]  # 第一个元素是版本号
                    # 假设日期紧跟在版本号之后，并且以方括号包围
                    date = version_parts[1] if version_parts[1].startswith('[') and version_parts[1].endswith(']') else ''
    
                # 查找下载链接
                download_buttons = list_div.find_next_siblings('div', class_='button')
                download_links = []
                for button in download_buttons:
                    for link in button.find_all('a', href=True):
                        if "便携版" in link.text:
                            full_url = requests.utils.urljoin(url, link['href'])
                            download_links.append({'href': full_url, 'text': link.text.strip()})
    
                # 将信息添加到列表
                if version and download_links:
                    combined_info.append({
                        'version': version,
                        'date': date,
                        'download_links': download_links
                    })
    
        # 将综合信息保存到JSON文件中
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(combined_info, f, ensure_ascii=False, indent=4)
    
        print("Combined information has been updated and saved to combined_info.json.")
        break
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        continue
