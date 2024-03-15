FROM python:3.13.0a4-alpine
MAINTAINER Rafa Muñoz rafa93m@gmail.com (@rafa93m)

RUN set -eux \
  && apk add --update --no-cache dcron libcap \
  && pip install --no-cache-dir pymongo \
  && pip install --no-cache-dir urllib3 \
  && pip install --no-cache-dir pytelegrambotapi \
  && pip install --no-cache-dir mqtthandler \
  && pip install --no-cache-dir dnspython 

COPY bot /opt/bot

RUN echo "****** Create user ******" && \
  addgroup -g 1000 -S storjnodemonitor && \
  adduser -u 1000 -S storjnodemonitor -G storjnodemonitor && \
  chown storjnodemonitor:storjnodemonitor /usr/sbin/crond && \
  setcap cap_setgid=ep /usr/sbin/crond && \
  mkdir /opt/bot/crontab && \
  echo "*    *    *    *    *    python3 /opt/bot/check_nodes.py" > /opt/bot/crontab/storjnodemonitor && \
  chown -R storjnodemonitor:storjnodemonitor /opt/bot && \
  chmod -R 744 /opt/bot

USER storjnodemonitor
WORKDIR /opt/bot

ENTRYPOINT ["/bin/sh","/opt/bot/docker-entrypoint.sh"]

CMD ["python3","/opt/bot/storjmonitor_bot.py"]
