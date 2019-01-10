# -*- coding = utf-8 -*-

from mongoengine import DynamicDocument, StringField, ListField, IntField, DictField


class User(DynamicDocument):
    """用户"""

    appkey = StringField(unique=True)

    appsecret = StringField()

    name = StringField()


class BrandByFirstLetter(DynamicDocument):
    """品牌"""

    # 品牌列表 长这个样 [{"brandid": 1, "brandname": "大众", "logo": "http://baidu.com/xixi.jpg"}]
    brand_list = ListField(unique=True)
    # 首字母
    first_letter = StringField()


class Brand(DynamicDocument):
    """品牌名和品牌id"""

    brand_name = StringField()
    brand_id = IntField()


class Series(DynamicDocument):
    """车系名和车系id"""

    series_name = StringField()
    series_id = StringField()
    brand_id = IntField()


class Spec(DynamicDocument):
    """车型名和车型id"""

    spec_name = StringField()
    spec_id = IntField()
    series_id = StringField()
    brand_id = IntField()


class SeriesByBrandId(DynamicDocument):
    """车系"""

    # 车系列表 长这个样 [{"item": [{"disable": True, "id": "xx", "leveid": 2, "name": "捷达", "pricebetween": ""}], "fcName": "大众"}]
    fct_list = ListField()
    # 品牌ID
    brand_id = IntField()
    # 品牌名
    brand_name = StringField()


class SpecBySeriesId(DynamicDocument):
    """车型"""

    # 车系ID
    series_id = StringField()
    series_name = StringField()
    # 总数
    spec_count = IntField()
    # 在售 长这个样 [{"Displacement":1.2,"FuelTypeId":1,"ISClassic":0,"ParamIsShow":1,"FlowmodeId":1,"Enginepower":85,"SpecList":[{"flowmodeid":1,"istaxrelief":0,"enginepower":85,"name":"2012款 1.2L实用型","ispreferential":0,"specisimage":0,"maxprice":37800,"order":1,"flowmodename":"自然吸气","state":20,"drivingmodename":"中置后驱","transmission":"5挡手动","isclassic":0,"minprice":37800,"logo":"http://car0.autoimg.cn/upload/spec/1001190/20120726171452518264.jpg","displacement":1.2,"year":2012,"fueltypeid":1,"paramisshow":1,"id":1001190}],"FlowmodeName":"自然吸气"}]
    spec_group_list = ListField()
    # 停售
    spec_stop_list = ListField()
    # 未售
    spec_upcoming_list = ListField()
    brand_id = IntField()
    brand_name = StringField()


class ConfigBySpecId(DynamicDocument):
    """配置"""

    spec_id = IntField()
    config = ListField()
    param = ListField()


class Maintenance(DynamicDocument):
    """保养数据"""

    MasterBrandName = StringField()
    MasterBrandID = IntField()
    FirstLetter = StringField()
    GroupName = StringField()
    GroupID = IntField()
    DefaulCarID = IntField()
    SerialAllSpell = StringField()
    SerialID = IntField()
    SerialName = StringField()
    # result = DictField()
    result = ListField()
    Logo = StringField()
