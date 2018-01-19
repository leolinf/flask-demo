# -*- coding: utf-8 -*-

from celery.bin import worker

from app import create_app, celery

app = create_app()
app.app_context().push()


if __name__ == '__main__':

    with app.app_context():
        worker = worker.worker(app=celery)

        worker.run(loglevel="info", queues=["anti_q", ])
