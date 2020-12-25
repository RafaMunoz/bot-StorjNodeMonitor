# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler
import random
import os
import mqtthandler
import time


def check_environ(env, default):
    """ Comprobamos las variables de entorno"""
    try:
        return os.environ[env]
    except KeyError:
        # print("Environment var {0} not found set {1}".format(env, default))
        return default


class LogRM(object):

    def __init__(self):
        """ Inicializamos variables"""
        # Comunes
        self.loglevel = check_environ("LOGLEVEL", "DEBUG").upper()
        self.idlog = check_environ("IDLOG", "Default")
        self.debug = 0
        self.enable_logfile = int(check_environ("ENABLE_LOGFILE", 0))
        self.enable_serverlog = int(check_environ("ENABLE_SERVERLOG", 0))
        self.pathlogfile = "log/{0}.log".format(self.idlog)
        self.server = check_environ("SERVERLOG", "localhost")
        self.port = int(check_environ("PORT_SL", 1883))
        self.username = check_environ("USER_SL", "guest")
        self.password = check_environ("PASS_SL", "guest")
        self.topic = check_environ("TOPIC_LOGS", "/logs")
        self.client_id = "logmqtt-client-{0}-{1}".format(self.idlog, random.randint(0, 10000))

    def init(self):
        self.logger = logging.getLogger(self.idlog)
        self.logger.setLevel(self.loglevel)
        self.formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
                                           datefmt="%Y-%m-%dT%H:%M:%S%z")

        self.consolehandler = logging.StreamHandler()
        self.consolehandler.setFormatter(self.formatter)
        self.logger.addHandler(self.consolehandler)

        # Logfile
        if self.enable_logfile == 1:
            self.printdebug("FileLog enabled")
            self.filehandler = TimedRotatingFileHandler(self.pathlogfile, when="d", interval=1, backupCount=1)
            self.filehandler.setFormatter(self.formatter)
            self.logger.addHandler(self.filehandler)

        # ServerLogs MQTT
        if self.enable_serverlog == 1:
            self.printdebug("ServerLogs MQTT enabled")
            self.mh = mqtthandler.MQTTHandler(host=self.server, port=self.port, client_id=self.client_id,
                                              topic=self.topic)
            self.mh.username_pw_set(username=self.username, password=self.password)
            self.mh.setFormatter(self.formatter)
            self.logger.addHandler(self.mh)
            self.mh.loop_start()
            time.sleep(1)

    def printdebug(self, msg):
        """ Imprimimos por pantalla si debug esta habilitado"""
        if self.debug > 0:
            print(msg)
