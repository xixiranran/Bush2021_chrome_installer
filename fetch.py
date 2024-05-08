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
            # version_info = list_div.find('p')  # 寻找<p>标签以获取版本信息
            # print("version_info:",version_info)
            # 寻找所有的<p>标签
            p_tags = soup.find_all('p')
    
            for p_tag in p_tags:
                # 检查是否包含版本号的格式 vX.X.X.X
                if p_tag.text.startswith('v') and p_tag.text.count('.') == 3:
                    # 提取版本号
                    version = p_tag.text.split()[0]
                    print("version:",version)
                    # 尝试提取日期，假设日期紧跟在版本号之后，并且以方括号包围
                    if ' [' in p_tag.text:
                        date = p_tag.text.split(' ')[-1].strip('[]')
                        print("date:",date)
    
                # 查找下载链接
                download_buttons = list_div.find_next_siblings('div', class_='button')
                download_links = []
                for button in download_buttons:
                    for link in button.find_all('a', href=True):
                        if "便携" in link.text:
                            full_url = requests.utils.urljoin(url, link['href'])
                            download_links.append({'href': full_url, 'text': link.text.strip()})
                            print("download_links:",download_links)
    
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
