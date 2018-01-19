from . import weibo
from . import views


weibo.add_url_rule('/get/weibo/info/', view_func=views.GetWeiboInfo.as_view('getweiboinfo'))
weibo.add_url_rule('/get/weibo/fri/', view_func=views.GetWeiboFri.as_view('getweibofri'))
weibo.add_url_rule('/get/weibo/vip/', view_func=views.GetWeiboVipInfo.as_view('getweibovip'))
