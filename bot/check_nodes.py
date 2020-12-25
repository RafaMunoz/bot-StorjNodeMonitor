#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import pymongo
import telebot
from comunes import *
from logrm import LogRM

print("------ Start Check Nodes ------")

# Settings
telegram_token = checkEnviron("TELEGRAM_TOKEN")
mongoconnection = checkEnviron("URI_MONGODB")

# Log
l = LogRM()
l.idlog = "{0}-{1}".format(l.idlog, "check")
l.init()
log = l.logger

# Bot telegram
bot = telebot.TeleBot(telegram_token)

# Connect to MongoDB
db = pymongo.MongoClient(mongoconnection).get_database()
users_col = db['users']
nodes_col = db['nodes']

# Search all nodes with notifications activated
nodes = nodes_col.find({"notifications": True})

for node in nodes:

    node_split = str(node["address"]).split(":")
    addr = node_split[0]
    port = node["check"]["port"]

    id_user = node["idUser"]
    datenow = datetime.utcnow()

    # Check if personalized downtime
    if "downtime" in node["check"]:
        downtime = int(node["check"]["downtime"])
    else:
        downtime = 3

    # Check the port
    try:
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        a_socket.settimeout(0.2)
        location = (addr, port)
        result_of_check = a_socket.connect_ex(location)
        a_socket.close()
    except Exception as f:
        log.error(location)
        log.error(f)
        continue

    # If the node returns to be active we send notification
    if result_of_check == 0:
        nodes_col.update_one({"idUser": id_user, "address": node["address"]},
                             {"$set": {"check.last": datenow, "check.last_ok": datenow, "check.error": 0,
                                       "check.send_error": False}})

        log.debug("Port is open {0}:{1} user {2}".format(addr, port, id_user))

        if node["check"]["send_error"]:
            message_text = "🟢 *Node UP* \n\nWe have detected that your node {0} is now *Online*!" \
                           "\n\n- Address: `{1}`\n- Port: " \
                           "`{2}`".format(node["name"], addr, port)

            log.debug("NODE UP for user: {0} node down {1}:{2} last_ok: "
                  "{3}".format(id_user, addr, port, node["check"]["last_ok"]))

            bot.send_message(chat_id=int(id_user), text=message_text, parse_mode='Markdown')

    else:
        errors = node["check"]["error"] + 1
        log.debug("CLOSE Port {0}:{1} user: {2} errors: {3}".format(addr, port, id_user, errors))

        # If errors >= downtime send user notification
        if errors >= downtime and not node["check"]["send_error"]:
            try:
                message_text = "⚠ *Node Down*\n\nWe have detected that your node *{0}* has been offline since" \
                               " {1} UTC+0.\nPlease check it!\n\n- Address: `{2}`\n- Port: " \
                               "`{3}`".format(node["name"], datetime.strftime(node["check"]["last_ok"], "%Y-%m-%d "
                                                                                                        "%H:%M:%S"),
                                              addr, port)

                log.info("Notification for user: {0} node down {1}:{2} last_ok: "
                      "{3}".format(id_user, addr, port, node["check"]["last_ok"]))

                bot.send_message(chat_id=int(id_user), text=message_text, parse_mode='Markdown')

                nodes_col.update_one({"idUser": id_user, "address": node["address"]},
                                     {"$set": {"check.last": datenow, "check.error": errors,
                                               "check.send_error": True}})

            except Exception as e:
                log.error(e)

        else:
            nodes_col.update_one({"idUser": id_user, "address": node["address"]},
                                 {"$set": {"check.last": datenow, "check.error": errors}})
