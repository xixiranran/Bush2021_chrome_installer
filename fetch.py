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

def decode(text):
    try:
        # 尝试解析XML数据
        root = tree.fromstring(text)
    except tree.ParseError as e:
        # 如果解析失败，打印错误信息
        print("An error occurred while parsing XML:", e)
        # 这里可以添加更多的错误处理逻辑，比如尝试修复数据或者退出函数
        # return None 或者 re-raise 异常等
        return None
    manifest_node = root.find('.//manifest')
    if manifest_node is None:
        print("Error: manifest_node is None")
        return
    #print("text:",text)
    #print("root:",root)
    #print("manifest_node:",manifest_node)
    manifest_version = manifest_node.get('version')
    
    package_node = root.find('.//package')
    package_name = package_node.get('name')
    package_size = int(package_node.get('size'))
    package_sha1 = package_node.get('hash')
    package_sha1 = base64.b64decode(package_sha1)
    package_sha1 = package_sha1.hex()
    package_sha256 = package_node.get('hash_sha256')

    url_nodes = root.findall('.//url')
    url = url_nodes[0].get('codebase') + package_name
    print("package_name:",package_name)
    print("package_size:",package_size)
    print("package_sha1:",package_sha1)
    print("package_sha256:",package_sha256)
    print("url:",url)

    
    # url_prefixes = []
    # for node in url_nodes:
    #     url_prefixes.append(node.get('codebase') + package_name)

    return {"version":manifest_version, "size":package_size, "sha1":package_sha1, "sha256":package_sha256, "url":url}
    
results = {}

def version_tuple(v):
    return tuple(map(int, (v.split("."))))

#暂时没有想到办法较少post请求次数。
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
                    # 从响应头中获取文件大小（字节）
                    file_size_bytes_str = res.headers.get('X-Goog-Stored-Content-Length', '0')
                    file_size_bytes = int(file_size_bytes_str)
                    
                    # 使用humansize函数获取用户友好的文件大小
                    file_size_human = humansize(file_size_bytes)
                    
                    print(f"文件大小: {file_size_human}")
                    
            # if "release" in k:
            #     data['label'] = "Release稳定版"
            # if "esr" in k:
            #     data['label'] = "Esr稳定版"
            # elif "beta" in k:
            #     data['label'] = "Beta测试版"
            # elif "devedition" in k:
            #     data['label'] = "Dev开发版"
            # elif "nightly" in k:
            #     data['label'] = "Nightly每夜版"
            # print("res:",res)
            #print("data2:",data)
            #print("results:",results)
            #下面的代码因为我把data.json的格式改了，所以执行有问题，且我想到一个问题，就是他这个判断是判断的stable版本有无更新，有更新才执行后面的代码，但是有可能stable没更新，其他版本有更新，这样就会导致更新不及时，所以索性注释掉这个代码，让他按github action设置的时间频率，每次执行的时候都重新生成data.json，而且注释这段代码github action执行后自己也会判断生成的文件有无变化，如果没变化则不自动更新生成
            #if version_tuple(data['version']) < version_tuple():
            #    print("ignore", k, data['version'])
            #    continue
            #print("data['time']:",data['time'])
            #print("results['data']['win_x86']1:",results['data']['win_x86'])
            # if version_tuple(results['data'][arch][k]['version']) < version_tuple(data['version']):
            #     print("results['data'][arch][k]['updatetime']:",arch,k,results['data'][arch][k]['updatetime'])
            #     data['updatetime'] = int(datetime.now().timestamp() * 1000)
            #     print("results['data'][arch][k]['version']:",arch,k,results['data'][arch][k]['version'])
            #     print("data['version']:",data['version'])
            #     print("data['updatetime']:",data['updatetime'])
                #如果版本有更新则输出更新的data的所有内容，如果版本号没更新就跳出本次循环，这样写是因为版本号请求有时候会变，一会变成新版本，一会又调到老版本了。这样写能保证data.json文件中的版本号是最新的。
                # results['data'][arch].update({k: data})
                # print("updated results['data'][arch][k]['version']:",k,results['data'][arch][k]['version'])
            # else:
            #     continue
                # data['updatetime'] = results['data']['win_x86'][k]['updatetime']

    #data.json里面win7的数据是固定不变的
    
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

