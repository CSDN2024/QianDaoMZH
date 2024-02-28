import json
import os

import requests

# 青龙面板环境变量中 注意大小写!
# comicai_Cookie 存放Cookie
# comicai_Token 存放Token

def dailyTask():
    comicai_Cookie=os.environ.get('comicai_Cookie')
    comicai_Token=os.environ.get('comicai_Token')

    headers = {
        'cookie': comicai_Cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.70 Safari/537.36'
    }

    session = requests.session()

    # 1.登录
    login_url = 'https://comicai.ai/signin'  # 登录url
    rep = session.get(url=login_url, headers=headers)  # rep是返回的网页源码
    # 检查响应状态码
    if rep.status_code == 200:
        # 获取文本格式的响应数据
        data_text = rep.text
        # print("rep-文本格式数据：", data_text) #<Response [200]>
    else:
        print("请求失败")

    # 2.查看分数
    check_mark_url = 'https://api.comicai.ai/api/v1/user/info'
    headers = {
        'Token': comicai_Token,
        #没有Token 会导致{"code":"AUTH_FAILED","message":"auth failed"}{'code': 'AUTH_FAILED', 'message': 'auth failed'}
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.70 Safari/537.36'
    }

    mark_rep = requests.get(check_mark_url, headers=headers)
    if mark_rep.status_code == 200:
        # 请求成功
        # 获取文本格式的响应数据
        # data_text = mark_rep.text
        # print("mark_rep-文本格式数据：{}".format(data_text) ) #<Response [200]>
        data_json = mark_rep.json()
        print("data_json-文本格式数据：{}".format(data_json))
        asset_mana = data_json['data']['asset']['mana']
        print("asset_mana-签到前的积分数：{}".format(asset_mana))
    else:
        # 请求失败
        print(f"签到前查询积分失败，状态码：{mark_rep.status_code}")

    # 3.签到
    sign_url = "https://api.comicai.ai/api/v1/user/sign"
    headers = {
        "Content-Type": "application/json", #如果注释了本行代码 请求失败 {'code': 'CODEC', 'message': 'unregister Content-Type: '}
        "Token": comicai_Token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36"
    }
    data = "{}"

    response = requests.post(sign_url, headers=headers, data=data)

    if response.status_code == 200:
        result = json.loads(response.text)
        if result.get("code") == "Success":
            mana = result["data"]["asset"]["mana"]
            print(f"签到成功,签到后得到的积分数 mana 值为: {mana}")
        elif result.get("code") == "USER_REPEAT_SIGN":
            print(f"今天已经签到过了,退出")
        else:
            print("签到请求失败")
            print(result)
    else:
        print(f"请求出错，错误码: {response.status_code}")


if __name__ == '__main__':
    dailyTask()
    print("执行完毕~")
