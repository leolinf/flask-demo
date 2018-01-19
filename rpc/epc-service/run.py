#! /usr/bin/env python
# -*- coding = utf-8 -*-

from argparse import Namespace

from nameko.cli.run import main


if __name__ == '__main__':
    args = Namespace(backdoor_port=None, config="settings.yaml", main=main, services=["wsgi"])
    main(args)
