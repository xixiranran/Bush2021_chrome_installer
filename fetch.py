import requests
import xml.etree.ElementTree as tree
import base64
import binascii
import json
from datetime import datetime, timezone
import time

info = {
    "win_x86": {
        "release": {
            "product": 'firefox-latest',
            "arch": 'win',
        },
        "esr": {
            "product": 'firefox-esr-latest',
            "arch": 'win',
        },
        "beta": {
            "product": 'firefox-beta-latest',
            "arch": 'win',
        },
        "dev": {
            "product": 'firefox-devedition-latest',
            "arch": 'win',
        },
        "nightly": {
            "product": 'firefox-nightly-latest',
            "arch": 'win',
        }
    },
    "win_x64": {
        "release": {
            "product": 'firefox-latest',
            "arch": 'win64',
        },
        "esr": {
            "product": 'firefox-esr-latest',
            "arch": 'win64',
        },
        "beta": {
            "product": 'firefox-beta-latest',
            "arch": 'win64',
        },
        "dev": {
            "product": 'firefox-devedition-latest',
            "arch": 'win64',
        },
        "nightly": {
            "product": 'firefox-nightly-latest',
            "arch": 'win64',
        }
    }
}

results = {}

# 解析响应头中的哈希值
def get_hashes(headers):
    hashes = {}
    # 正则表达式匹配crc32c和md5哈希值
    for part in headers['X-Goog-Hash'].split(','):
        hash_type, hash_value_encrypted = part.split('=', 1)  # 确保只分割一次

        # 计算需要添加的等号数量以使长度成为4的倍数
        padding = '=' * ((4 - len(hash_value_encrypted) % 4) % 4)
        
        # 尝试Base64解码哈希值
        try:
            hash_value_bytes = base64.b64decode(hash_value_encrypted + padding)
        except binascii.Error as e:
            print(f"Base64解码错误：{e}")
            continue  # 如果解码出错，跳过当前哈希值

        # 将字节数据转换为十六进制表示的字符串
        hash_value = hash_value_bytes.hex()

        hashes[hash_type] = hash_value
    return hashes

def fetch():
    global results
    while True:
        try:
            with open('data.json', 'r') as f:
                results = json.load(f)
                break
        except FileNotFoundError:
            print(f"data.json文件不存在。")
        except PermissionError:
            print(f"没有权限读取data.json文件。")
        except json.JSONDecodeError:
            print(f"data.json文件包含无效的JSON格式。")
        except Exception as e:
            print(f"读取文件时发生了一个错误：{e}")
        time.sleep(1)
        
    #请求服务器获取数据并更新到data.json的win_x86字典中
    for arch in ['win_x86', 'win_x64']:
        for k, v in info[arch].items():
            while True:
                url = f"https://download.mozilla.org/?product={v['product']}&os={v['arch']}&lang=zh-CN"
                # print("url:",url)   #https://download.mozilla.org/?product=firefox-latest&os=win&lang=zh-CN
                res = requests.get(url,allow_redirects=True)
                # print("res:",res)   #<Response [200]>
                if res.status_code == 200:
                    # print("res.headers:",res.headers)   #res.headers: {'Server': 'nginx', 'X-Goog-Generation': '1714395240799132', 'X-Goog-Metageneration': '1', 'X-Goog-Stored-Content-Encoding': 'identity', 'X-Goog-Stored-Content-Length': '61054664', 'X-Goog-Hash': 'crc32c=JToq+w==, md5=FmHraRZkw0Nv0GQSdYJltA==', 'X-Goog-Storage-Class': 'STANDARD', 'Accept-Ranges': 'bytes', 'X-Guploader-Uploadid': 'ABPtcPqDSc0d_Lf0EwhU0UAdZJXLlInBZXYJclg-MlohY95PPsofScUVGmSqZyb7qC2cFyNKf68', 'Strict-Transport-Security': 'max-age=31536000', 'Alt-Svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000, clear', 'Via': '1.1 google, 1.1 google', 'Date': 'Tue, 30 Apr 2024 11:19:01 GMT', 'Expires': 'Tue, 30 Apr 2024 15:19:01 GMT', 'Cache-Control': 'max-age=14400', 'Age': '14143', 'Last-Modified': 'Mon, 29 Apr 2024 12:54:00 GMT', 'ETag': '"1661eb691664c3436fd06412758265b4"', 'Content-Type': 'application/x-msdos-program', 'Vary': 'Origin', 'Content-Length': '61054664'}
                    # print("res.download_url:",res.url)   #res.download_url: https://download-installer.cdn.mozilla.net/pub/firefox/releases/125.0.3/win32/zh-CN/Firefox%20Setup%20125.0.3.exe
                    break
                else:
                    print(f"请求失败，状态码：{response.status_code}")
                    continue
            #获取下载链接
            # print("res.download_url:",res.url)
            results['data'][arch][k]['url'] = res.url
            
            # 从响应头中获取文件大小（字节）
            file_size_bytes_str = res.headers.get('X-Goog-Stored-Content-Length', '0')
            file_size_bytes = int(file_size_bytes_str)
            
            # 使用humansize函数获取用户友好的文件大小
            file_size_human = humansize(file_size_bytes)
            results['data'][arch][k]['size'] = file_size_human
            # print(f"文件大小: {file_size_human}")

            # 获取哈希值
            hashes = get_hashes(res.headers)
            
            # 打印结果
            results['data'][arch][k]['crc32c'] = hashes.get('crc32c')
            results['data'][arch][k]['md5'] = hashes.get('md5')
            # print(f"CRC32C Hash: {hashes.get('crc32c')}")
            # print(f"MD5 Hash: {hashes.get('md5')}")
            
            if "release" in k:
                results['data'][arch][k]['label'] = "Release稳定版"
            if "esr" in k:
                results['data'][arch][k]['label'] = "Esr稳定版"
            elif "beta" in k:
                results['data'][arch][k]['label'] = "Beta测试版"
            elif "devedition" in k:
                results['data'][arch][k]['label'] = "Dev开发版"
            elif "nightly" in k:
                results['data'][arch][k]['label'] = "Nightly每夜版"
    #获取最新时间并更新到data.json的time字典中
    results.update({'time': int(datetime.now().timestamp() * 1000)})
    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

fetch()
