# author: Ray-Eldath
# source: https://gist.github.com/Ray-Eldath/2e3a8052dcf558df17aa2b0215b22cb1


import json
import os
import sqlite3

import requests
from lxml import etree
import urllib

lang = 0  # 语言：0 汉语, 1 日语, 2 韩语, 3 英语
targets = ['艾尔海森','流浪者','珐露珊','莱依拉','纳西妲','妮露','坎蒂丝','赛诺','多莉','提纳里','柯莱','夜兰','瑶瑶']  # 角色名



def lift(x):
    assert len(x) == 1
    return x[0]


def select(doc, val, sub='list'):
    return lift([e[sub] for e in doc if e['name'] == val])


def extract_lang_id(doc):
    languages = ['汉语', '日语', '韩语', '英语']
    return lift(doc.xpath(f'//ul[@data-target="voiceTab.attr"][1]/li[text()="{languages[lang]}"]/@data-index'))


def extract_voice_lines(doc, lang_idx):
    tbody_xpath = f'//li[@data-index="{lang_idx}"]/table[@class="obc-tmpl-character__voice-pc"]/tbody'
    titles = doc.xpath(f'{tbody_xpath}/tr/td[@class="h3"]/text()')
    voice_xpath = f'{tbody_xpath}/tr/td/div[@class="obc-tmpl-character__voice-item obc-tmpl-character__play-voice"]'
    lines = [e.strip() for e in doc.xpath(f'{voice_xpath}/span/text()')]
    audios = doc.xpath(f'{voice_xpath}/div/audio/source/@src')
    assert len(titles) == len(lines) == len(audios)
    return zip(titles, lines, audios)


if __name__ == '__main__':

    # 连接数据库
    db = sqlite3.connect('./db/character.db')
    cursor = db.cursor()
    
    home_url = 'https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/home/content/list?app_sn=ys_obc&channel_id=189'
    home = requests.get(home_url).json()['data']['list']
    handbook = select(home, '图鉴', sub='children')
    character = select(handbook, '角色')
    content_ids = [e['content_id'] for e in character if e['title'] in targets]
    assert len(content_ids) == len(targets)
    for cid in content_ids:
        detail_url = f"https://api-static.mihoyo.com/common/blackboard/ys_obc/v1/content/info?app_sn=ys_obc&content_id={cid}"
        print(detail_url)
        detail = requests.get(detail_url).json()['data']['content']
        print(f"{detail['title']} - {detail['summary']}")
        html = etree.HTML(select(detail['contents'], '角色展示', sub='text'))
        idx = extract_lang_id(html)
        print('    lang_idx: ', idx)
        for res in extract_voice_lines(html, idx):
            # print(f'    {res[0]}: {"".join(res[1].splitlines())} {res[2]}')
            
            # 将音频文件下载到 ./res/audio/{detail["title"]} 目录下
            
            # 如果文件夹不存在则创建
            if not os.path.exists(f'./res/audio/{detail["title"]}'):
                os.makedirs(f'./res/audio/{detail["title"]}')
            # 将音频文件保存到本地,  如果文件存在则跳过
            if not os.path.exists(f'./res/audio/{detail["title"]}/{str(res[2]).split("/")[-1]}'):
                with open(f'./res/audio/{detail["title"]}/{str(res[2]).split("/")[-1]}', 'wb') as f:
                    audio = requests.get(res[2])
                    f.write(audio.content)
            
            # 将数据插入到 ./db/character.db 中
            url = "https://raw.githubusercontent.com/CSUSTers/mys-voice-genshin/main/res/audio/{}/{}".format(urllib.parse.quote(detail['title']),str(res[2]).split('/')[-1].replace('.mp3', '.ogg'))
            sql = f"INSERT INTO character (character, topic, text, audio) VALUES ('{detail['title']}', '{res[0]}', '{res[1]}', '{url}')"
            print(sql)
            cursor.execute(sql)
    db.commit()
    db.close()


