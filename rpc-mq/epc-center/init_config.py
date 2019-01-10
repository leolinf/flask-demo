#! /usr/bin/env python
# -*- coding = utf-8 -*-

import json

from app import create_app
from app.models import SpecBySeriesId, Spec, ConfigBySpecId


def main():

    filename = "car.info.4.20170927"

    l = []
    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = json.loads(line)
            spec_id = line["type_id"]
            config = line["config"]
            param = line["param"]
            l.append(ConfigBySpecId(spec_id=spec_id, config=config, param=param))
            if len(l) > 500:
                ConfigBySpecId.objects.insert(l)
                l = []

        ConfigBySpecId.objects.insert(l)


if __name__ == '__main__':
    create_app()
    main()
