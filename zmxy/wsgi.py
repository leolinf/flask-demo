# -*- coding: utf-8 -*-

from app import create_app


application = create_app()


if __name__ == '__main__':

    application.run(port=8887, debug=True)
