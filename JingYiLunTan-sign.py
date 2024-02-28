import os

import requests
import re
import time
from lxml import etree


def dailyTask():
    JYLT_Cookie=os.environ.get('JYLT_Cookie')


    headers = {
        'cookie':JYLT_Cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    }

    session = requests.session()

    url_page = 'https://bbs.125.la/plugin.php?id=dsu_paulsign:sign'
    #1.登录得到帖子
    rep = session.get(url=url_page, headers=headers)#rep是返回的网页源码

    hot_message = re.findall(r'/thread-14(.*).html" target="_blank"', rep.text)#获取首页热门的帖子地址
    # print(hot_message)
    #['812294-1-1', '812481-1-1', '812254-1-1', '812156-1-1', '812348-1-1', '812474-1-1', '812182-1-1', '812359-1-1', '812267-1-1', '812159-1-1', '810464-1-1', '810459-1-1', '810334-1-1', '808876-1-1', '807810-1-1', '766025-1-1', '777673-1-1', '793375-1-1', '783395-1-1', '804966-1-1']

    formhash = re.findall(r'formhash=(.*)">退出', rep.text)
    print("formhash:{}".format(formhash))#['e5eexxxx]

    # formhash=xxxxxxx 看起来是一个表单提交时的参数。
    # formhash 是一个用于防止 CSRF（跨站请求伪造）攻击的安全令牌,也是后面签到需要用到的参数。
    url_page = 'https://bbs.125.la/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1'
    #2.自动签到
    rep = session.post(url=url_page, headers=headers,
                       data={'formhash': formhash, "submit": "1", "targerurl": "", "todaysay": "", "qdxq": "kx"})
    print("签到结果:" + re.findall(r'{"status":0,"msg":"(.*)"}', rep.text)[0])

    #3.自动评分
    for i in range(0, len(hot_message)):
        url_page = 'https://bbs.125.la/thread-14' + hot_message[i] +'.html'
        rep = session.get(url=url_page, headers=headers)
        if rep.status_code == 200:
            print('进入帖子详情页成功')
            tree = etree.HTML(rep.text)
            a_list = tree.xpath('//*[@id="ak_rate"]/@onclick')
            addr = a_list[0]
            str1 = addr.split(',')
            str2 = str1[1].split('&')
            tid1 = str2[2]
            pid1 = str2[3]
            tid2 = tid1.split('=')[1]
            pid2 = pid1.split('=')[1]
            pid3 = pid2.split('\'')[0]
            tid = tid2
            pid = pid3  # 获取到tid与pid
            formash1 = tree.xpath('//*[@id="vfastpost"]/input/@value')
            formash = formash1[0]  # 获取到formash
            # print("获取pid={}与tid={}与formash={}成功，开始自动评分".format(pid, tid, formash))
            # 开始评分
            url_score = 'https://bbs.125.la/forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1'
            data = 'formhash=' + formash + '&tid=' + tid + '&pid=' + pid + '&referer=https%3A%2F%2Fbbs.125.la%2Fforum.php%3Fmod%3Dviewthread%26tid%3D' + tid + '%26page%3D0%23pid' + pid + '&handlekey=rate&score4=%2B1&reason=%E6%84%9F%E8%B0%A2%E5%88%86%E4%BA%AB%EF%BC%8C%E5%BE%88%E7%BB%99%E5%8A%9B%EF%BC%81%7E'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Referer'] = 'https://bbs.125.la/thread-14720892-1-1.html'

            rep_score = session.post(url=url_score, data=data, headers=headers) #开始评分请求,rep_score是评分返回的源码

            rep_score_result=rep_score.status_code # 200表示评分成功
            if rep_score_result==200:
                print("评分推送成功,任务:{}".format(i))
            else:
                print("评分推送失败,任务:{}".format(i))


            score_message=re.findall(r'CDATA\[(.*)<scrip', rep_score.text)[0]
            result = re.search(r'class="showmenu">积分: (\d+)</a>', rep.text)
            if result:
                number = result.group(1)  # 提取匹配到的数字部分
                print("评分反馈:{},积分:{}".format(score_message,number))
            else:
                number=-1
                print("未找到匹配的内容,积分:{}".format(number))

            time.sleep(2)
            error_limit = rep_score.text.find("超过限制")
            if error_limit != -1:
                print("已经完成评分次数{},24小时评分数超过限制,退出".format(i))
                break;
        else:
            print('进入帖子失败')


if __name__ == '__main__':
    dailyTask()
    print("执行完毕~")