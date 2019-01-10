# -*- coding = utf-8 -*-

from app.common.parser import base_parser_get, base_parser_post
from app.common.validator import vin, json_type

car_structure_parser = base_parser_get.copy()
car_structure_parser.add_argument("vin", location="args", required=True, type=vin)
