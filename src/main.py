from base64 import encode
import os
import requests
import re

import urllib

# 读取characterInfo.txt文件，放入字符串中
def read_file():
    with open('./res/characterInfo.txt', 'r', encoding='UTF-8') as f:
        data = f.read()
    return data

# 从characterInfo.txt中获取所有角色的id
def get_id():
    CharacterData = read_file()
    # 正则匹配其中的文本
    CharacterPattern = r'style="width:23.50%;"><a title="(.*?)" href="/ys/obc/content'
    UrlPattern = r'" href="/ys/obc/content/(\d+\.?\d*)/detail'
    # 使用两个正则表达式匹配 CharacterData
    CharacterList = re.findall(CharacterPattern, CharacterData)
    UrlList = re.findall(UrlPattern, CharacterData)
    # 将匹配到的文本放入字典中
    CharacterDict = {}
    for i in range(len(CharacterList)):
        CharacterDict[CharacterList[i]] = UrlList[i]
    # 将字典中的数据写入文件
    with open('./res/characterUrlDict.txt', 'w') as f:
        for key in CharacterDict:
            f.write(key + '\n')
            f.write(CharacterDict[key] + '\n')
    CharacterDict.pop('安柏 角色语音(CV：牛奶君)')
    CharacterDict.pop('菲谢尔 角色语音（CV：Mace&amp;赵悦程）')
    return CharacterDict

# 从characterUrlDict中获取每个角色的语音，存入csv中
def get_url():
    CharacterDict = get_id()
    for key in CharacterDict:
        urlBase = 'https://bbs.mihoyo.com/ys/obc/content/{}/detail'.format(CharacterDict[key])
        # get请求urlbase获取页面
        html = requests.get(urlBase).text
        # 正则匹配页面中的文本
        # 语音话题标题
        topicPattern = r'obc-tmpl__rich-text obc-tmpl-fold__title"><p style="white-space: pre-wrap;">(.*?)</p></div> <div class="obc-tmpl__paragraph-box obc-tmp'
        # 语音音频文件
        audioPattern = r'ss="audio"><audio controls="controls" controlslist="nodownload"><source src="(.*?)"'
        # 语音话题文本
        textPattern = r'"></audio></span></p><p style="white-space: pre-wrap;">(.*?)</p></div> <div class="obc-tmpl__fold-tag">'
        # 匹配
        topic = re.findall(topicPattern, html)
        audio = re.findall(audioPattern, html)
        text = re.findall(textPattern, html)
        # 打印数量不一致的情况
        if(len(topic) != len(audio) or len(topic) != len(text)):
            print('=================================')
            print(key.replace(' 角色语音', ''))
            print('topic: ', len(topic), 'audio: ', len(audio), 'text: ', len(text))
        # 将匹配到的数据写入csv文件

        # 去掉空哥的语音
        if key == '旅行者 角色语音':
            with open('./res/{}.csv'.format(key.replace(' 角色语音', '')), 'w', encoding='UTF-8') as f:
                f.write('topic,text,audio\n')
                for i in range(len(topic)):
                    try:
                        f.write(topic[i] + ',' + text[i].replace('</p><p style="white-space: pre-wrap;">','<br>') + ',' + audio[i*2] + '\n')
                    except Exception as e:
                        pass
        else:
            with open('./res/{}.csv'.format(key.replace(' 角色语音', '')), 'w', encoding='UTF-8') as f:
                f.write('topic,text,audio\n')
                for i in range(len(topic)):
                    try:
                        f.write(topic[i] + ',' + text[i].replace('</p><p style="white-space: pre-wrap;">','<br>').replace(',','，') + ',' + audio[i] + '\n')
                    except Exception as e:
                        pass

# 从csv拉取文件到本地
def get_file():
    # 读取res/csv下的所有csv文件
    for file in os.listdir('./res/csv'):
        if file.endswith('.csv'):
            print(file)
            # 使用pandas读取csv文件
            import pandas as pd
            df = pd.read_csv('./res/csv/{}'.format(file))
            urlList = df['audio'].tolist()
            # 遍历urlList，下载语音
            for url in urlList:
                if url != 'None':
                    try:
                        # 如果文件夹不存在，则创建文件夹
                        if not os.path.exists('./res/audio/{}'.format(file.replace('.csv', ''))):
                            os.mkdir('./res/audio/{}'.format(file.replace('.csv', '')))
                        # 如果文件不存在，则下载语音
                        if not os.path.exists('./res/audio/{}/{}'.format(file.replace('.csv', ''), url.split('/')[-1])):
                            with open('./res/audio/{}/{}'.format(file.replace('.csv', ''), url.split('/')[-1]), 'wb') as f:
                                audioFile = requests.get(url).content
                                f.write(audioFile)
                    except Exception as e:
                        print(e)
                        print(url)

# 获取res/audio目录下的所有mp3格式文件，并调用ffmpeg编码为opus编码器ogg格式
def get_opus(crrDir):
    # 读取res/audio下的所有mp3文件
    for file in os.listdir(crrDir):
        if file.endswith('.mp3'):
            print(file)
            # 调用ffmpeg编码ogg格式
            os.system('ffmpeg -i '+crrDir+'/{} -c:a libopus -b:a 96K  '.format(file) +crrDir+'/{}.ogg'.format(file.replace('.mp3', '')))

# 创建一个sqlLite数据库，用于保存csv中的数据
def create_db():
    import sqlite3
    conn = sqlite3.connect('./db/character.db')
    c = conn.cursor()
    # 创建一个表，用于保存角色的语音
    c.execute('''CREATE TABLE character
            (id integer primary key autoincrement, character text, topic text, text text, audio text)''')
    conn.commit()
    conn.close()

# 将csv中的数据导入到数据库中
def insert_db():
    import sqlite3
    conn = sqlite3.connect('./db/character.db')
    c = conn.cursor()
    # 读取res/csv下的所有csv文件
    for file in os.listdir('./res/csv'):
        if file.endswith('.csv'):
            print(file)
            # 使用pandas读取csv文件
            import pandas as pd
            df = pd.read_csv('./res/csv/{}'.format(file))
            # 遍历csv文件，将数据插入到数据库中
            for i in range(len(df)):
                sql = "INSERT INTO character (character, topic, text, audio) VALUES ('{}', '{}', '{}', '{}')".format(file.replace('.csv', ''), df['topic'][i], df['text'][i], "https://raw.githubusercontent.com/CSUSTers/mys-voice-genshin/main/res/audio/{}/{}".format(urllib.parse.quote(file.replace('.csv', '')),str(df['audio'][i]).split('/')[-1].replace('.mp3', '.ogg')))
                print(sql)
                c.execute(sql)
            
    conn.commit()
    conn.close()

# main函数，请按需调用上面的函数
if __name__ == '__main__':
    # 创建数据库，并导入数据
    create_db()
    insert_db()
    
