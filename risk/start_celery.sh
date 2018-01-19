service filebeat start
su user -c 'celery -A celery_app.celery worker -B -f /var/log/riskctrlpy_celery.log -Q unlock_q,monitor_q,sms_q,anti_q -c 2 -s /tmp/xxx.beat'
