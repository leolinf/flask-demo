# -*- coding = utf-8 -*-

import abc
import logging
import urllib.parse

import requests
from nameko.exceptions import RpcTimeout, MethodNotFound, UnknownService
from nameko.standalone.rpc import ServiceRpcProxy

from app import Config
from app.common.constant import Params, BrandFirstThreeLetter


class Service(metaclass=abc.ABCMeta):

    ERROR = {"result": "error"}
    TIMEOUT = Config.TIMEOUT
    INVALID = {"result": "invalid"}

    @property
    def logger(self):

        return logging.getLogger(self.__class__.__name__)


class HttpService(Service, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def authenticate(self):
        pass

    def make_request(self, url, method="GET", req=None):

        self.logger.info("正在请求 {0}".format(url))

        if method == "POST":
            no_need_key = [Params.SIGN, Params.APPKEY, Params.TIMESTAMP]
            for key in no_need_key:
                if key in req:
                    req.pop(key)
            try:
                r = requests.post(url, json=req, timeout=self.TIMEOUT)
            except Exception as e:
                self.logger.exception(e)
                return self.ERROR

        elif method == "GET":
            try:
                r = requests.get(url, timeout=self.TIMEOUT)
            except Exception as e:
                self.logger.exception(e)
                return self.ERROR

        else:
            self.logger.exception("不支持的方法 {0}".format(method))
            return self.ERROR

        try:
            return r.json()
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("错误时的返回结果 {0}".format(r.text))

        return self.ERROR


class NamekoService(Service, metaclass=abc.ABCMeta):

    AMQP_URI = Config.NAMEKO_AMQP_URI

    @property
    @abc.abstractmethod
    def service_name(self):
        pass

    def make_rpc(self, method_name, req):

        """
        :type method_name: str
        :type req: dict

        :param method_name: 对应rpc服务的方法名
        :param req: 请求的参数
        """

        # 去掉不必要的参数
        no_need_key = [Params.SIGN, Params.APPKEY, Params.TIMESTAMP]
        for key in no_need_key:
            if key in req:
                req.pop(key)

        try:
            with ServiceRpcProxy(self.service_name, config={"AMQP_URI": self.AMQP_URI}, timeout=self.TIMEOUT) as \
                    service:
                resp = getattr(service, method_name)(**req)
                if isinstance(resp, dict) and "data" in resp:
                    resp = resp["data"]

                return resp
        except RpcTimeout:
            self.logger.error("超时")
        except UnknownService:
            self.logger.error("没有对应服务\t{0}".format(self.service_name))
        except MethodNotFound:
            self.logger.error("该服务没有对应方法\t{0}".format(method_name))
        except Exception as e:
            self.logger.exception(e)

        return self.ERROR

    def get_car_structure_info(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_STRUCTURE_INFO, req)

    def get_car_parts_info(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_PARTS_INFO, req)

    def get_car_fuzzy_query(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_FUZZY_QUERY, req)

    def get_car_model_search(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_MODEL_SEARCH, req)

    def get_car_model(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_MODEL, req)

    def get_car_parts(self, req):

        return self.INVALID

    def get_car_structure(self, req):

        return self.INVALID

    def get_all_parts_info(self, req):

        return self.make_rpc(Config.NAMEKO_CAR_ALL_PARTS_INFO, req)


class ServiceProxy(object):

    def __init__(self, req):

        """
        :type req: dict

        :param req: 请求的参数
        """
        self.req = req
        self.vin = req["vin"]
        self.invalid = False
        self.service = self.init_service()

    @staticmethod
    def _get_service(vin):

        service_map = {
            "WDB": BenzService,
            "WDC": BenzService,
            "S35": BenzService,
            "LB1": BenzService,
            "LE4": BenzService,
            "2HM": HyundaiService,
            "KMH": HyundaiService,
            "LNB": HyundaiService,
            "LBE": HyundaiService,
            "LFV": VolkswagenService,
            "LSV": VolkswagenService,
            "LNW": VolkswagenService,
            "WVW": VolkswagenService,
            "WUA": VolkswagenService,
            "WAU": VolkswagenService,
            "TRU": VolkswagenService,
            "LHG": HondaService,
            "JHG": HondaService,
            "LUC": HondaService,
            "JHM": HondaService,
            "LVH": HondaService,
            "JH4": HondaService,
        }

        def _update_map(letter, service_name):

            nonlocal service_map
            service_map[letter] = service_name

        [_update_map(k, ToyotaService) for k in BrandFirstThreeLetter.TOYOTA]
        [_update_map(k, NissanService) for k in BrandFirstThreeLetter.NISSAN]

        return service_map.get(vin[:3], None)

    def init_service(self):

        service = self._get_service(self.vin)
        if service is None:
            self.invalid = True
            return
        else:
            return service(self.req)

    def get_car_structure(self):

        return self.service.get_car_structure(self.req)

    def get_car_parts(self):

        return self.service.get_car_parts(self.req)

    def get_car_structure_info(self):

        return self.service.get_car_structure_info(self.req)

    def get_car_parts_info(self):

        return self.service.get_car_parts_info(self.req)

    def get_car_fuzzy_query(self):

        return self.service.get_car_fuzzy_query(self.req)

    def get_car_model_search(self):

        return self.service.get_car_model_search(self.req)

    def get_car_model(self):

        return self.service.get_car_model(self.req)

    def get_all_parts_info(self):

        return self.service.get_all_parts_info(self.req)

    @property
    def error(self):

        return self.service.ERROR

    @property
    def result_invalid(self):
        return self.service.INVALID


class NissanService(NamekoService):

    def __init__(self, req):

        self.req = req

    @property
    def service_name(self):

        return Config.NAMEKO_SERVICE_NISSAN

    def get_car_fuzzy_query(self, req):

        return self.INVALID

    def get_car_model_search(self, req):

        return self.INVALID
