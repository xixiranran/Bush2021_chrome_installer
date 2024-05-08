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
            # 提取版本号和日期
            p_tag = list_div.find('p')
            if p_tag and 'v' in p_tag.text:
                version = p_tag.text.split('v')[1].split()[0]
                # date = p_tag.text.split(' ')[-1].strip('[]').strip()
                # 提取日期，注意日期紧跟在'<i>'标签之后，并以'</i>'结束
                date_match = p_tag.text.split('<i>')[1].split('</i>')[0]
                date = date_match.strip()
    
            # 在同一.list div中查找.button div以获取下载链接
            button_div = list_div.find('div', class_='button')
            # print("button_div:",button_div)
            if button_div:
                download_links = []
                for link in button_div.find_all('a', href=True):
                    if "便携" in link.text:
                        full_url = urljoin(url, link['href'])
                        # print("full_url:",full_url)
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
