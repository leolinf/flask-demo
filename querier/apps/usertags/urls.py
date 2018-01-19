# -*- coding: utf-8 -*-
from . import usertags
from . import views


usertags.add_url_rule(
    "/get/user/tags/", view_func=views.GetUserTags.as_view('gettags')
)
usertags.add_url_rule(
    "/portrait/tags/get/", view_func=views.PortraitView.as_view('PortraitView')
)
usertags.add_url_rule(
    "/portrait/tags/three/get/", view_func=views.ThreePortrait.as_view('ThreePortraitView')
)
