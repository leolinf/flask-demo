# coding=utf8
import jieba.analyse
import requests
import json
from framework.logger import project_logger
from time import time


def get_statuses_timeline(uid, count=100, timeout=1):
    '''
    抓取最新5条微博, 返回微博列表
    '''
    url = 'https://api.weibo.com/2/statuses/user_timeline.json?source=3538199806&count={}&feature=1&page=1&trim_user=1&uid={}'.format(
        count, uid)
    try:
        r = requests.get(url, timeout=1)
    except requests.exceptions.Timeout:
        return ""
    return r.text


def weibo_keywords(uid):
    start_time = time()
    try:
        statuses = json.loads(get_statuses_timeline(uid))
    except ValueError:
        return []
    sentence = '\n'.join([x['text'] for x in statuses['statuses']])
    keywords = jieba.analyse.textrank(
        sentence, topK=50, withWeight=True, allowPOS=('n'))
    project_logger.info("[GET][WEIBO][KEYWORD][TIME|%s][REQUEST|%s][RESPONSE|%s]", time()-start_time, uid, keywords)
    # keywords 是需要的
    if keywords:
        return [{"name":keyword[0], "value": keyword[1]} for keyword in keywords]
    else:
        return []
