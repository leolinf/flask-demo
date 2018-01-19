from app.config import Config
from nameko.rpc import rpc
from app.logger import project_logger
from .service import nissan_structure, nissan_parts_get, nissan_car_model, nissan_all_parts


class NissanStructure:

    name = Config.CAR_NISSAN

    @rpc
    def car_model(self, vin):
        """车型查询"""

        project_logger.info("[structure][NISSAN][VIN|%s]", vin)
        response = nissan_car_model(vin)
        return response

    @rpc
    def structure_info(self, vin):
        """二级三级目录查询"""

        project_logger.info("[structure][NISSAN][VIN|%s]", vin)
        response = nissan_structure(vin)
        return response

    @rpc
    def parts_info(self, vin, search: dict):
        """配件查询"""

        project_logger.info("[parts][NISSAN][VIN|%s][SEARCH|%s]", vin, search)
        response = nissan_parts_get(search)
        return response

    @rpc
    def all_parts_info(self, vin):
        """查询所有配件"""

        response = nissan_all_parts(vin)
        project_logger.info("[parts][NISSAN][VIN|%s]", vin)
        return response
