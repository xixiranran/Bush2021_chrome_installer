import requests
import xml.etree.ElementTree as tree
import base64
import binascii
import json
from datetime import datetime, timezone
import time

info = {
    "win_x86": {
        "stable": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{C6CB981E-DB30-4876-8639-109F8933582C}"''',
            "apVersion": '''"x86-ni"''',
        },
        "beta": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{CB2150F2-595F-4633-891A-E39720CE0531}"''',
            "apVersion": '''"x86-dev"''',
        },
        "dev": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{103BD053-949B-43A8-9120-2E424887DE11}"''',
            "apVersion": '''"x86-be"''',
        },
        "nightly": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{AFE6A462-C574-4B8A-AF43-4CC60DF4563B}"''',
            "apVersion": '''"x86-rel"''',
        }
    },
    "win_x64": {
        "stable": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{C6CB981E-DB30-4876-8639-109F8933582C}"''',
            "apVersion": '''"x64-ni"''',
        },
        "beta": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{CB2150F2-595F-4633-891A-E39720CE0531}"''',
            "apVersion": '''"x64-dev"''',
        },
        "dev": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{103BD053-949B-43A8-9120-2E424887DE11}"''',
            "apVersion": '''"x64-be"''',
        },
        "nightly": {
            'bid': '''"{11111111-1111-1111-1111-111111111111}"''',
            "appid": '''"{AFE6A462-C574-4B8A-AF43-4CC60DF4563B}"''',
            "apVersion": '''"x64-rel"''',
        }
    }
}

update_url = 'https://updates.bravesoftware.com/service/update2'

session = requests.Session()


def post(bid: str, appid: str, apVersion: str) -> str:
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <request protocol="3.0" version="1.3.99.0" shell_version="1.3.99.0" ismachine="1" sessionid={bid} installsource="taggedmi" testsource="auto" requestid={bid} dedup="cr">
    <os platform="win" version="" sp="" arch="x86"/>
    <app appid={appid} version="" nextversion="" ap={apVersion} lang="en" brand="" client="" installage="-1" installdate="-1">
    <updatecheck/>
    </app>
    </request>'''
    
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'User-Agent': 'Google Update/1.3.101.0;winhttp'
    # }
    
    r = session.post(update_url, data=xml)
    # r = session.post(update_url, data=xml, headers=headers, verify=False)
    # print("Request Headers:", r.request.headers)
    # print("Request Body:", r.request.body)
    # print("Response Status Code:", r.status_code)
    # print("Response Headers:", r.headers)
    # print("Response Body:", r.text)
    return r.text

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
def fetchandsavejson():
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
            #print("k:",k)     #stable
            print("v:",v)
            # print("v:",v)     #{'os': 'platform="win" version="10.0" sp="" arch="x86"', 'app': 'appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" version="" nextversion="" lang="en" brand=""  installage="-1" installdate="-1" iid="{11111111-1111-1111-1111-111111111111}"'}
            #print("info['win_x86']:",info['win_x86'])
            #print("info['win_x86'].items():",info['win_x86'].items())
            #下面while true是为了解决post偶尔抽风得到的数据为none时，解决AttributeError: 'NoneType'对象没有'get'属性的问题
            # 设置一个循环，当响应不为None时停止
            while True:
                # 发送POST请求
                res = post(**v)
                data = decode(res)
                if data is None:
                    print("Error: decode返回为None",arch,k)
                    continue
                else:
                    break
                    
            if "stable" in k:
                data['label'] = "Stable 稳定版"
            elif "beta" in k:
                data['label'] = "Beta 测试版"
            elif "dev" in k:
                data['label'] = "Dev 开发版"
            elif "nightly" in k:
                data['label'] = "Nightly 每夜版"
            #print("res:",res)
            #print("data2:",data)
            #print("results:",results)
            #下面的代码因为我把data.json的格式改了，所以执行有问题，且我想到一个问题，就是他这个判断是判断的stable版本有无更新，有更新才执行后面的代码，但是有可能stable没更新，其他版本有更新，这样就会导致更新不及时，所以索性注释掉这个代码，让他按github action设置的时间频率，每次执行的时候都重新生成data.json，而且注释这段代码github action执行后自己也会判断生成的文件有无变化，如果没变化则不自动更新生成
            #if version_tuple(data['version']) < version_tuple():
            #    print("ignore", k, data['version'])
            #    continue
            #print("data['time']:",data['time'])
            #print("results['data']['win_x86']1:",results['data']['win_x86'])
            if version_tuple(results['data'][arch][k]['version']) < version_tuple(data['version']):
                print("results['data'][arch][k]['updatetime']:",arch,k,results['data'][arch][k]['updatetime'])
                data['updatetime'] = int(datetime.now().timestamp() * 1000)
                print("results['data'][arch][k]['version']:",arch,k,results['data'][arch][k]['version'])
                print("data['version']:",data['version'])
                print("data['updatetime']:",data['updatetime'])
                #如果版本有更新则输出更新的data的所有内容，如果版本号没更新就跳出本次循环，这样写是因为版本号请求有时候会变，一会变成新版本，一会又调到老版本了。这样写能保证data.json文件中的版本号是最新的。
                results['data'][arch].update({k: data})
                print("updated results['data'][arch][k]['version']:",k,results['data'][arch][k]['version'])
                with open('data.json', 'w') as f:
                    json.dump(results, f, indent=4)
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

fetchandsavejson()

