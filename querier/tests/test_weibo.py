# -*- coding: utf-8 -*-

import sys
sys.path.append("../")

import unittest
import json
from app import app


class TelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_weibo_info(self):
        rv = self.client.get('/get/weibo/info/?telno=13402879377&username=2312348662&password=oaxidu7ap0jt4vaivjfuxc6yd4x5p69g')
        assert rv.status_code == 200
        assert json.loads(rv.data).get("code") == 1200

    def test_weibo_fri(self):
        rv = self.client.get('/get/weibo/fri/?telno=13402879377&username=2312348662&password=oaxidu7ap0jt4vaivjfuxc6yd4x5p69g')
        assert rv.status_code == 200
        assert json.loads(rv.data).get("code") == 1200

    def test_weibo_vip(self):
        data = {"ids": 124345345}
        rv = self.client.post('/get/weibo/vip/?username=2312348662&password=oaxidu7ap0jt4vaivjfuxc6yd4x5p69g', data=data)
        assert rv.status_code == 200
        assert json.loads(rv.data).get("code") == 1200


if __name__ == '__main__':
    unittest.main()
