# -*- coding: utf-8 -*-


class Code:
    """错误码"""

    SUCCESS = 10000

    MSG = {
        SUCCESS: u'成功',
    }

    ERROR_MSG = {
        1: "正确",
        0: "一般错误，或者未单独列出的错误，默认错误",
        1001: "内部错误，授权异常，请稍后再试",
        1002: "请求超时(请求app超时, 网络出现问题, 或app不存在)",
        1006: "未查找到任务(可能是因为操作超时任务丢失，目前设定超时时间为5分钟)",
        1008: "请求参数错误(请参考步骤)",
        2101: "获取验证码错误, 请检查账号情况(淘宝返回的其它账号异常情况，目前未捕获到的异常情况)",
        2102: "获取验证码异常，请稍后重新尝试(发送短信异常)",
        2103: "发送短信验证码失败(发送短信请求返回异常)",
        2104: "该账号不存在或未开通手机登录，请检查后再试(你的账户可能未开启手机登录功能，请更换其他登录方式。 账户不存在或该账户未绑定手机号，请更换其他登录方式 。)",
        2106: "出现滑块验证(为了你的账户安全，请点击滑块上的圆圈完成验证。 )",
        2107: "发送短信次数达到上限, 请15分钟后再试(获取次数已达上限，请15分钟后再试)",
        2108: "发送短信次数达到上限, 请明天再试(获取次数已达上限，请明天再试)",
        2110: "访问淘宝页面异常(请求登录页面失败, 或登录页面结构改变)",
        2202: "登录异常, 请稍后重新尝试(淘宝页面返回的其他异常, 具体异常由返回的",
        2203: "淘宝端登录超时错误，请稍后重新尝试(淘宝提示错误页面)",
        2204: "短信验证码错误(返回信息为验证码已失效或验证码错误)",
        2206: "初始化session失败，请稍后重新尝试(授权完成生成采集session, 并初始化异常)",
        2207: "帐号异常(账户存在安全风险，已被限制登录，请在电脑上登录淘宝网，根据提示操作)",
        2208: "系统错误(授权成功, 连接采集队列失败, 导致无法采集)",
        }

    CODE_MSG = {
        41000:"成功",
        41501:"没有传递必要参数",
        41502:"服务器出错",
        41503:"请求超时",
        41504:"查询中",
        41505:"查询成功没数据",
        41506:"该账号不存在或未开通手机登录，请检查后再试",
        41507:"token 不存在",
        41508:"授权成功，正在提取数据中",
        41508:"授权成功，正在提取数据中",
        41510:"sms code",
        41511:"任务不存在",
        41512:"登录异常",
        41513:"短信验证错误",
        41514:"账户异常，请15分钟后重试",
        41515:"短信验证码获取次数上线请15分钟后重试",
        41516:"短信验证码获取次数上线请明天重试",
        41517:"授权失败",
        41518:"手机号错误",

    }