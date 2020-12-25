FROM python:3.8-alpine
MAINTAINER Rafa Muñoz rafa93m@gmail.com (@rafa93m)

RUN set -eux \
  && pip install --no-cache-dir pymongo \
  && pip install --no-cache-dir urllib3 \
  && pip install --no-cache-dir pytelegrambotapi \
  && pip install --no-cache-dir mqtthandler

RUN mkdir /opt/bot
COPY bot /opt/bot
RUN chmod -R 644 /opt/bot

RUN echo "*    *       *       *       *       python3 /opt/bot/check_nodes.py" >> /etc/crontabs/root

WORKDIR /opt/bot

ENTRYPOINT ["/bin/sh","/opt/bot/docker-entrypoint.sh"]

CMD ["python3","/opt/bot/storjmonitor_bot.py"]