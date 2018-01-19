# -*-coding:utf-8 -*-

from Queue import Queue
from threading import Thread

from utils.data import gen_dec_refers_by_kv, get_weibo_tags_by_tid
from utils.auth import (get_weibo_info, get_weibo_key, get_weibo_link,
                        get_weibo_fri, get_weibo_info_all, get_weibo_link_all)

from framework.logger import project_logger
from time import time


def get_friend_info(follow_ids):
    """
    批量获取好友的基本数据
    weibo_infos = get_weibo_info_all([int(wid) for wid in ids])
    weibo_links = get_weibo_link_all([int(wid) for wid in ids])
    """

    if follow_ids:
        start_time = time()

        res = []
        link = {}
        try:
            ids = follow_ids.split(",")
        except AttributeError:
            ids = [str(follow_ids)]
        args = [int(wid) for wid in ids]

#        result_queue = Queue()
#        func_queue = Queue()
#        func_queue.put(get_weibo_info_all)
#        func_queue.put(get_weibo_link_all)
#
#        def _func(q, args):
#            func = func_queue.get()
#            q.put({func.__name__: func(args)})
#            func_queue.task_done()
#        for i in range(func_queue.qsize()):
#            Thread(target=_func, args=(result_queue, args)).start()
#
#        func_queue.join()
#        result_dict = {}
#        while not result_queue.empty():
#            result_dict.update(result_queue.get())
#
#        weibo_infos = result_dict.get("get_weibo_info_all")
#        weibo_links = result_dict.get("get_weibo_link_all")

        weibo_infos = get_weibo_info_all(args)
        project_logger.info("[GET][WEIBO_INFOS_ALL][TIME|%s]", time() - start_time)
        limit_list = [i.get("weibo_id") for i in weibo_infos]
        weibo_links = get_weibo_link_all(limit_list)
        project_logger.info("[GET][WEIBO_LINK_ALL][TIME|%s]", time() - start_time)

        for weibo_link in weibo_links:
            link[weibo_link["weibo_id"]] = weibo_link["follow_ids"]
        for info in weibo_infos:
            info["follow_ids"] = link.get(info.get("weibo_id"))
            res.append(info)
        project_logger.info("[GET][WEIBO_INFO_ALL][TIME|%s]", time() - start_time)
        return res
    return None


def weibo_info(telno):
    """查询weibo的基本信息和key"""

    refers = gen_dec_refers_by_kv('tel', telno)
    if refers:
        res = []
        start_time = time()
        weibo_id = set([i[-1] for i in refers])
        for wid in weibo_id:
            try:
                wid = int(wid)
            except:
                wid = wid
            weibo_info = get_weibo_info(wid)
            weibo_key = get_weibo_key(wid)
            weibo_link = get_weibo_link(wid)
            friend_info = None
            if weibo_link:
                friend_info = get_friend_info(weibo_link.get("follow_ids"))
            res.append({"weibo_info": weibo_info, "weibo_key": weibo_key,
                        "weibo_link": weibo_link, "friend_info": friend_info})
        project_logger.info("[GET][WEIBO_INFO][TIME|%s][REQUEST|%s]", time() - start_time, telno)
        return res
    return None


def weibo_fri(telno):
    """查询接口snwb_fri"""

    refers = gen_dec_refers_by_kv('tel', telno)
    if refers:
        res = []
        start_time = time()
        weibo_id = set([i[-1] for i in refers])
        if not weibo_id:
            return None
        for wid in weibo_id:
            weibo_fris = get_weibo_tags_by_tid(wid)
            mud_time = time()
            project_logger.info("[GET][SNWB_FRI|HBSE][TIME|%s][REQUEST|%s]", mud_time - start_time, telno)
            #for weibo_fri in weibo_fris:
            data = get_weibo_fri([int(i) for i in weibo_fris])
            for i in data:
                res.append(i)
        project_logger.info("[GET][SNWB_FRI][TIME|%s][REQUEST|%s]", time() - mud_time, telno)
        return res
    return None
