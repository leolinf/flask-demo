from . import electric
from . import views


electric.add_url_rule('/get/tels/', view_func=views.GetTelList.as_view('gettels'))
electric.add_url_rule('/get/old/tels/', view_func=views.GetOldTelList.as_view('getoldtels'))
electric.add_url_rule('/get/tel/tag/', view_func=views.GetTelTag.as_view('gettags'))
