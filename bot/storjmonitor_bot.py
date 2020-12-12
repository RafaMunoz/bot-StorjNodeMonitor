#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymongo
import telebot
from comunes import *
from keyboards import *


# Function user information
def infouser(message, tp="message"):
    id_user = message.from_user.id
    name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    registration_date = datetime.utcnow()

    if tp == "callback":
        text = message.data
    else:
        text = message.text

    user_document = {
        '_id': str(id_user),
        'username': username,
        'name': name,
        'lastName': last_name,
        'registrationDate': registration_date,
        'lastAccess': registration_date,
        'lastMessage': {
            'type': '',
            'idMessage': '',
            'text': ''
        },
        'contact': False
    }

    if tp == "callback":
        print("New callback -> id_user: {0}, username: {1}, callback: {2}".format(id_user, username, text))
    else:
        print("New Message -> id_user: {0}, username: {1}, message: {2}".format(id_user, username, text))

    updatelastaccess(id_user)

    return user_document


# Check if the user exist in db
def checkuser(userdoc):
    try:
        userdoc_db = users_col.find_one({"_id": userdoc['_id']})
        if userdoc_db is None:
            users_col.insert_one(userdoc)
            print("New user: {0}".format(userdoc))

        else:
            return userdoc_db

    except Exception as a:
        print("Failed to save new user to database {0}".format(userdoc))
        print(a)


# Update last access
def updatelastaccess(id_user):
    try:
        users_col.update_one({"_id": str(id_user)}, {"$set": {"lastAccess": datetime.utcnow()}})
    except Exception as b:
        print("Failed to update last access for user {0}".format(id_user))
        print(b)


print("------ Start Bot ------")

# Settings
telegram_token = checkEnviron("TELEGRAM_TOKEN")
mongoconnection = checkEnviron("URI_MONGODB")

try:
    id_admin = int(os.environ["ID_ADMIN"])
except KeyError:
    id_admin = 0

# Bot telegram
bot = telebot.TeleBot(telegram_token)

# Connect to MongoDB
db = pymongo.MongoClient(mongoconnection).get_database()
users_col = db['users']
nodes_col = db['nodes']

main_message = "I can help you check the statistics of your *Storj Nodes* and send you notifications if I lose " \
               "connection with any of them.\n\nYou can control me by sending these commands:\n\n/newnode - create a " \
               "new node\n/mynodes - see all your nodes\n\n*Edit Nodes*\n/setname - Change a node's name\n" \
               "/setaddress - Change a node's address\n/deletenode - Delete a node\n\n*Stats*\n/seestats - View " \
               "Stats\n\n*Notifications*\n/enablenotification - Enable node status " \
               "notifications\n/disablenotification - Disable node status notifications.\n\nIf you have any questions" \
               " or have discovered a bug in the bot you can use the command /contact"


# ---------- Comands ----------

# Command /start create new user if not exists and send message
@bot.message_handler(commands=['start'])
def command_start(message):
    checkuser(infouser(message))
    bot.send_message(message.chat.id, main_message, parse_mode="Markdown")


# Message for command /mynodes
@bot.message_handler(commands=['mynodes'])
def message_myaddrs(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})
    print("Send keyboard myNodes to user: {0}".format(infouser_db['_id']))

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Nodes User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="Choose a Node from the list below:",
                         reply_markup=keyboardNodes(nodes, 'mynode-', False))


# Message for command /newnode
@bot.message_handler(commands=['newnode'])
def message_newnode(message):
    infouser_db = checkuser(infouser(message))
    response = bot.send_message(chat_id=infouser_db['_id'],
                                text="Alright, a new node. How are we going to call it? Please choose a name for your "
                                     "node.",
                                parse_mode='Markdown')
    users_col.update_one({"_id": str(infouser_db['_id'])},
                         {"$set": {"lastMessage.type": "newnode", "lastMessage.idMessage": str(response.message_id)}})


# Message for command /setname
@bot.message_handler(commands=['setname'])
def message_setname(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="Choose the address to which you want to change the name.",
                         reply_markup=keyboardNodes(nodes, 'setNodeName-', False), parse_mode='Markdown')


# Message for command /setaddress
@bot.message_handler(commands=['setaddress'])
def message_setaddr(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="Choose the address to which you want to change the code.",
                         reply_markup=keyboardNodes(nodes, 'setNodeAddr-', False))


# Message for command /deleteaddr
@bot.message_handler(commands=['deletenode'])
def message_deleteaddr(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="Choose a node to delete.",
                         reply_markup=keyboardNodes(nodes, 'delNode-', False), parse_mode='Markdown')


# Message for command /enablenotification
@bot.message_handler(commands=['enablenotification'])
def message_enablenotification(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'],
                         text="Choose the Node you want to - *Activate* - notifications:",
                         reply_markup=keyboardNodes(nodes, 'notON-', False), parse_mode='Markdown')


# Message for command /disablenotification
@bot.message_handler(commands=['disablenotification'])
def message_disablenotification(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="Choose the Node you want to - *Disable* - notifications:",
                         reply_markup=keyboardNodes(nodes, 'notOFF-', False), parse_mode='Markdown')


# Message for command /seestats
@bot.message_handler(commands=['seestats'])
def message_seestats(message):
    infouser_db = checkuser(infouser(message))
    print("Search nodes for user: {0}".format(infouser_db['_id']))
    nodes = nodes_col.find({"idUser": infouser_db['_id']})

    if nodes.explain()['executionStats']['nReturned'] == 0:
        print("Found 0 Address User: {0}".format(infouser_db['_id']))
        bot.send_message(chat_id=infouser_db['_id'],
                         text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a new "
                              u"node.")

    else:
        bot.send_message(chat_id=infouser_db['_id'], text="From which node do you want to check the statistics?",
                         reply_markup=keyboardNodes(nodes, 'stats-', False), parse_mode='Markdown')


# Message for command /contact
# Envia teclado inline al mandar comando /contactar
@bot.message_handler(commands=['contact'])
def message_contact(message):
    infouser_db = checkuser(infouser(message))
    users_col.update_one({"_id": str(infouser_db['_id'])}, {"$set": {"contact": True}}, upsert=True)

    mensaje = "Please write your message to contact:"
    bot.send_message(message.chat.id, mensaje, parse_mode="Markdown", reply_markup=keyboardCancelContact())


# Proccess message text
@bot.message_handler(func=lambda message: True)
def message_other(message):
    infouser_db = checkuser(infouser(message))

    # Insert name for new node
    if infouser_db['lastMessage']['type'] == 'newnode':

        response = bot.send_message(chat_id=infouser_db['_id'],
                                    text="Good. Now, indicate the address to check the statistics of your node. So "
                                         "for example: n01.mydomain.com:14002",
                                    parse_mode='Markdown')
        users_col.update_one({"_id": str(infouser_db['_id'])}, {
            "$set": {"lastMessage.type": "newnodeaddr", "lastMessage.idMessage": str(response.message_id),
                     "lastMessage.text": message.text}})

        print(
            "Save the name node on lastMessage -> idUser: {0}, nameNode: {1}".format(infouser_db['_id'], message.text))

    # Insert address for new node
    elif infouser_db['lastMessage']['type'] == 'newnodeaddr':
        
        address_node = cleanString(message.text)

        nodes_col.insert_one(
            {'name': infouser_db['lastMessage']['text'], "address": address_node, "idUser": infouser_db['_id'],
             "notifications": False,
             "check": {"port": 28967, "last": datetime.utcnow(), "last_ok": datetime.utcnow(), "error": 0,
                       "send_error": False}})

        users_col.update_one({"_id": str(infouser_db['_id'])},
                             {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})
        print('Insert new node -> idUser: {0}, nameNode: {1}, address: {2}'.format(infouser_db['_id'],
                                                                                   infouser_db['lastMessage']['text'],
                                                                                   address_node))

        message_new_node = "Done! Congratulations for your new node.\n\nNow you can start checking your statistics, " \
                           "run the /seestats command and choose your node.\n\nName: `{0}`\n" \
                           "Address: `{1}`".format(infouser_db['lastMessage']['text'], address_node)
        bot.send_message(chat_id=infouser_db['_id'], text=message_new_node, parse_mode='Markdown',
                         reply_markup=keyboardReturnMyNodes())

    # Edit address name
    elif infouser_db['lastMessage']['type'] == 'setnodename':

        nodes_col.update_one({"idUser": str(infouser_db['_id']), "address": infouser_db['lastMessage']['text']},
                             {"$set": {"name": message.text}})
        users_col.update_one({"_id": str(infouser_db['_id'])},
                             {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        print("Update name node. user: {0} node: {1} new_name: {2}".format(infouser_db['_id'],
                                                                           infouser_db['lastMessage']['text'],
                                                                           message.text))

        info_node = nodes_col.find_one(
            {'idUser': str(infouser_db['_id']), "address": infouser_db['lastMessage']['text']})

        message_update_nodename = "Your node name has been updated.\n\n*Node*: `{0}`\n*Address*: `{1}`".format(
            info_node['name'], info_node['address'])
        bot.send_message(chat_id=infouser_db['_id'], text=message_update_nodename, parse_mode='Markdown',
                         reply_markup=keyboardReturn(info_node['address']))

    # Edit address node
    elif infouser_db['lastMessage']['type'] == 'setnodeaddr':

        nodes_col.update_one({"idUser": str(infouser_db['_id']), "address": infouser_db['lastMessage']['text']},
                             {"$set": {"address": message.text}})
        users_col.update_one({"_id": str(infouser_db['_id'])},
                             {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        print("Update address node. user: {0} node: {1} new_name: {2}".format(infouser_db['_id'],
                                                                              infouser_db['lastMessage']['text'],
                                                                              message.text))

        info_node = nodes_col.find_one({'idUser': str(infouser_db['_id']), "address": message.text})

        message_update_nodename = "Your node address has been updated.\n\n*Node*: `{0}`\n*Address*: `{1}`".format(
            info_node['name'], info_node['address'])
        bot.send_message(chat_id=infouser_db['_id'], text=message_update_nodename, parse_mode='Markdown',
                         reply_markup=keyboardReturn(info_node['address']))

    # Edit address port check notifications
    elif infouser_db['lastMessage']['type'] == 'changeport':

        try:
            port = int(message.text)
            nodes_col.update_one({"idUser": str(infouser_db['_id']), "address": infouser_db['lastMessage']['text']},
                                 {"$set": {"check.port": port}})

            users_col.update_one({"_id": str(infouser_db['_id'])},
                                 {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "",
                                           "lastMessage.text": ""}})

            split_addr = infouser_db['lastMessage']['text'].split(":")

            print("Update port check. user: {0} node: {1} new_port: {2}".format(infouser_db['_id'], split_addr[0],
                                                                                message.text))

            message_text = "The port has been changed. Now we will carry out the checks at:\n- Address: {0}\n- " \
                           "Port: {1}".format(split_addr[0], port)

        except Exception as d:
            print(d)
            message_text = "🔴 An error occurred while updating the information. Check that the port is only made up " \
                           "of numbers or try again later."

        bot.send_message(chat_id=infouser_db['_id'], text=message_text, parse_mode='Markdown',
                         reply_markup=keyboardReturnCustom(prefix="notNode-",
                                                           node_code=infouser_db['lastMessage']['text']))

    # Edit downtime notifications
    elif infouser_db['lastMessage']['type'] == 'changedowntime':

        try:
            downtime = int(message.text)

            if downtime == 0:
                downtime = 3

            nodes_col.update_one({"idUser": str(infouser_db['_id']), "address": infouser_db['lastMessage']['text']},
                                 {"$set": {"check.downtime": downtime}})

            users_col.update_one({"_id": str(infouser_db['_id'])},
                                 {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "",
                                           "lastMessage.text": ""}})

            split_addr = infouser_db['lastMessage']['text'].split(":")

            print("Update downtime. user: {0} node: {1} downtime: {2}".format(infouser_db['_id'], split_addr[0],
                                                                              downtime))

            message_text = "The downtime has been changed. Now we will send the notification:\n- Address: {0}\n- " \
                           "Downtime: {1} minutes".format(split_addr[0], downtime)

        except Exception as d:
            print(d)
            message_text = "🔴 An error occurred while updating the information. Check that the downtime is only made " \
                           "up of numbers or try again later. If you send a 0 downtime, the default value of 3 " \
                           "minutes will be set."

        bot.send_message(chat_id=infouser_db['_id'], text=message_text, parse_mode='Markdown',
                         reply_markup=keyboardReturnCustom(prefix="notNode-",
                                                           node_code=infouser_db['lastMessage']['text']))

    # Check if message if for contact
    elif infouser_db['contact']:
        users_col.update_one({"_id": str(infouser_db['_id'])}, {"$set": {"contact": False}}, upsert=True)

        message_text = "Thank you very much for contacting me. We will read your message as soon as possible."
        bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

        message_admin = "------ New Message ------\nID: {0}\nName: {1}\nMessage: " \
                        "{2}".format(message.from_user.id, message.from_user.first_name, message.text)

        try:
            bot.send_message(id_admin, message_admin, parse_mode="Markdown")
            print("Send message to ID: {0} Name: {1} Message: "
                  "{2}".format(message.from_user.id, message.from_user.first_name, message.text))

        except Exception as f:
            print(f)

    else:
        bot.send_message(message.chat.id, main_message, parse_mode="Markdown")


# -----------------------------

# ---------- Callbacks ----------

# Callback from inlinekeyboards
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    infouser_db = checkuser(infouser(call, tp="callback"))

    # Send keyboard options node
    if re.search("^mynode-+", call.data):
        print("Send keyboard options nodes to user: {0}".format(infouser_db['_id']))

        node_code = str(call.data).replace('mynode-', '')
        doc = nodes_col.find_one({"address": node_code, "idUser": infouser_db['_id']})
        node_name = doc['name']
        notifications = doc['notifications']

        text_notification = "Disabled"

        if notifications:
            text_notification = "Enabled"

        message_text = "Here it is:\n\n- *Node*: `{0}`\n- *Address*: `{1}`\n- *Notifications*: {2}\n\nWhat do you" \
                       " want to do with this node?".format(node_name, node_code, text_notification)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardOptionsNode(node_code))

    # Return to keyboardNodes
    elif call.data == "myNodes":
        print("Return to keyboardNodes, search nodes for user: {0}".format(infouser_db['_id']))
        nodes = nodes_col.find({"idUser": infouser_db['_id']})

        if nodes_col.count_documents({"idUser": infouser_db['_id']}) == 0:
            print("Found 0 Nodes to user: {0}".format(infouser_db['_id']))
            bot.send_message(chat_id=infouser_db['_id'],
                             text=u"\u26A0 You have not added an Node yet.\nYou can use the /newnode command to add a "
                                  u"new node.")
        else:
            print("Send keyboardNodes to user: {0}".format(infouser_db['_id']))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Choose a Node from the list below:", parse_mode='Markdown')
            bot.edit_message_reply_markup(chat_id=infouser_db['_id'], message_id=call.message.message_id,
                                          reply_markup=keyboardNodes(nodes, 'mynode-', False))

    # Callback for send keyboard to edit node
    elif re.search("^editNode-+", call.data):
        node_code = str(call.data).replace('editNode-', '')

        print("Send keyboardEditNode to user: {0}".format(infouser_db['_id']))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Select an option:", parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardEditNode(node_code))

    # Callback edit name for node
    elif re.search("^setNodeName-+", call.data):
        node_code = str(call.data).replace('setNodeName-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="OK. Send me the new name for your node.", parse_mode='Markdown')

        print("Update lastMessage.type -> setnodename user: {0} node: {1}".format(infouser_db['_id'], node_code))
        users_col.update_one({"_id": str(infouser_db['_id'])}, {
            "$set": {"lastMessage.type": "setnodename", "lastMessage.idMessage": str(call.message.message_id),
                     "lastMessage.text": node_code}})

    # Callback edit address for node
    elif re.search("^setNodeAddr-+", call.data):
        node_address = str(call.data).replace('setNodeAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="OK. Send me the new address for your node.", parse_mode='Markdown')

        print("Update lastMessage.type -> setnodeaddr user: {0} node: {1}".format(infouser_db['_id'], node_address))
        users_col.update_one({"_id": str(infouser_db['_id'])}, {
            "$set": {"lastMessage.type": "setnodeaddr", "lastMessage.idMessage": str(call.message.message_id),
                     "lastMessage.text": node_address}})

    # Callback to delete address
    elif re.search("^delNode-+", call.data):
        node_code = str(call.data).replace('delNode-', '')
        node_name = (nodes_col.find_one({"address": node_code, "idUser": infouser_db['_id']}))['name']

        message_text = "Are you sure you want to delete the following node?\n\n- *Node*: `{0}`\n- " \
                       "*Address*: `{1}`".format(node_name, node_code)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardDeleteNode(node_code))

    # Callback confirmed delete address
    elif re.search("^yesDelNode-+", call.data):
        node_code = str(call.data).replace('yesDelNode-', '')
        print("Delete node: {0} user: {1}".format(node_code, infouser_db['_id']))
        nodes_col.delete_one({"address": node_code, "idUser": infouser_db['_id']})

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Node deleted correctly.", parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyNodes())

    # Callback notificatios
    elif re.search("^notNode-+", call.data):
        node_code = str(call.data).replace('notNode-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Activating the notification service will receive a message every time there "
                                   "is a change of status in your *Node*.\n\nBy default we check port `28967` every  "
                                   "minute and we will notify if three failed checks occur. You can change it from "
                                   "the *Change Port* and *Change Downtime* buttons.", parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardNotifications(node_code))

    # Callabck activate notifications
    elif re.search("^notON-+", call.data):
        node_code = str(call.data).replace('notON-', '')
        node_name = (nodes_col.find_one({"address": node_code, "idUser": infouser_db['_id']}))['name']
        print("Activate notifications for: user -> {0} node ->{1}".format(infouser_db['_id'], node_code))
        nodes_col.update_one({"address": node_code, "idUser": infouser_db['_id']}, {"$set": {"notifications": True}})

        message_text = "Status notifications: ON 🟢\nNode: {0}".format(node_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyNodes())

    # Callback desactivate notificationes
    elif re.search("^notOFF-+", call.data):
        node_code = str(call.data).replace('notOFF-', '')
        node_name = (nodes_col.find_one({"address": node_code, "idUser": infouser_db['_id']}))['name']
        print("Desactivate notifications for: user -> {0} address ->{1}".format(infouser_db['_id'], node_code))
        nodes_col.update_one({"address": node_code, "idUser": infouser_db['_id']}, {"$set": {"notifications": False}})

        message_text = "Status notifications: OFF 🔴\nNode: {0}".format(node_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyNodes())

    # Callback stats
    elif re.search("^stats-+", call.data):
        node_code = str(call.data).replace('stats-', '')

        print("Get {0}/api/sno to user: {1}".format(node_code, infouser_db['_id']))
        try:
            req = requestAPI("{0}/api/sno/".format(node_code))
            started_at = convertDate(req["startedAt"])
            last_pinged = convertDate(req["lastPinged"])
            disk_available = req["diskSpace"]["available"]
            disk_used = req["diskSpace"]["used"]
            disk_trash = req["diskSpace"]["trash"]
            disk_free = disk_available - disk_used - disk_trash
            now = datetime.utcnow()
            str_last_pinged = pretty_date(now - last_pinged)
            str_uptime = pretty_date(now - started_at)

            status = nodes_col.find_one({"idUser": infouser_db['_id'], "address": node_code})

            if status["check"]["error"] == 0:
                color_status = "🟢"
            elif status["check"]["error"] == 1:
                color_status = "🟡"
            elif status["check"]["error"] == 2:
                color_status = "🟠"
            else:
                color_status = "🔴"

            message_text = "*--- Node Info ---*\n\n_Status:_ {2}\n_Uptime:_ {0}\n_Last Contact:_ {1}\n\n" \
                           "*Total Disk Space {3}*\n_Used:_ {4}\n_Free:_ {5}\n_Trash:_ " \
                           "{6}".format(str_uptime, str_last_pinged, color_status, convertSize(disk_available),
                                        convertSize(disk_used), convertSize(disk_free), convertSize(disk_trash))
            print("Send information Node Info to user: {0}".format(infouser_db['_id']))

        except Exception as c:
            print(c)
            message_text = "*--- Node Info ---*\n\n🔴 An error occurred while getting the information, try again later" \
                           " or check your node."

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardNodeInfo(node_code))

    # Callback utilization & remaining
    elif re.search("^utilization-+", call.data):
        node_code = str(call.data).replace('utilization-', '')

        print("Get {0}/api/sno/satellites to user: {1}".format(node_code, infouser_db['_id']))
        try:
            req = requestAPI("{0}/api/sno/satellites".format(node_code))
            message_text = "*--- Utilization & Remaining ---*\n\n" + statsString(req)
            print("Send Utilization & Remaining to user: {0}".format(infouser_db['_id']))

        except Exception as c:
            print(c)
            message_text = "*--- Utilization & Remaining ---*\n\n🔴 An error occurred while getting the information," \
                           " try again later or check your node."

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardNodeInfoSatellites(node_code))

    # Callback satellites
    elif re.search("^satellites-+", call.data):
        node_code = str(call.data).replace('satellites-', '')

        print("Get {0}/api/sno/ to user: {1}".format(node_code, infouser_db['_id']))
        try:
            req = requestAPI("{0}/api/sno/".format(node_code))
            print("Send keyboardSatellites to user: {0}".format(infouser_db['_id']))

            message_text = "Select a satellite to check its statistics"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                                  parse_mode='Markdown')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardSatellites(node_code, req))

        except Exception as c:
            print(c)

    # Callback Uptime & Audits
    elif re.search("^uptimeaudits-+", call.data):
        node_code = str(call.data).replace('uptimeaudits-', '')
        message_text = ""
        warning = ""

        try:
            # Get all satellites
            req = requestAPI("{0}/api/sno/".format(node_code))

            for satellite in req["satellites"]:
                satellite_id = satellite["id"]
                satellite_name = satellite["url"]

                if satellite["disqualified"] is not None:
                    warning = "\n\n⚠ Satellite disqualified node.\n"
                if satellite["suspended"] is not None:
                    warning = "\n\n⚠ Satellite suspended node.\n"

                # Get statistics satellite
                req2 = requestAPI("{0}/api/sno/satellite/{1}".format(node_code, satellite_id))

                # Get percentage
                uptime_total_count = req2["uptime"]["totalCount"]
                uptime_success_count = req2["uptime"]["successCount"]
                uptime_checks = percentage(uptime_success_count, uptime_total_count)

                audit_total_count = req2["audit"]["totalCount"]
                audit_success_count = req2["audit"]["successCount"]
                audit_checks = percentage(audit_success_count, audit_total_count)

                message_text = message_text + "🛰️ *{0}*\n_Uptime Checks_: *{1}%*\n_Audit Checks_: *{2}%*\n" \
                                              "{3}\n".format(satellite_name, uptime_checks, audit_checks, warning)

            print("Send info uptime and audit to user {0} node {1}".format(infouser_db['_id'], node_code))

        except Exception as c:
            print(c)
            message_text = "*--- Other Info ---*\n\n🔴 An error occurred while getting the information, try again " \
                           "later or check your node. "

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnCustom("utilization-", node_code))

    # Callback one satellite
    elif re.search("^sat-+", call.data):
        clean = str(call.data).replace('sat-', '')
        clean_split = clean.split("#")
        node_code = clean_split[0]
        n_stellite = clean_split[1]

        print("Get satellite id {0}/api/sno/ to user: {1}".format(node_code, infouser_db['_id']))
        try:
            # Get id for satellite
            req = requestAPI("{0}/api/sno/".format(node_code))
            satellite_id = req["satellites"][int(n_stellite)]["id"]

            # Check is satellite desqualified or suspended
            warning = ""
            if req["satellites"][int(n_stellite)]["disqualified"] is not None:
                warning = "\n\n⚠ {0}\n".format(req["satellites"][int(n_stellite)]["disqualified"])
            if req["satellites"][int(n_stellite)]["suspended"] is not None:
                warning = "\n\n⚠ {0}\n".format(req["satellites"][int(n_stellite)]["suspended"])

            # Get statistics satellite
            print("Get info satellite {0}/api/sno/satellite/{1} to user: {2}".format(node_code, satellite_id,
                                                                                     infouser_db['_id']))
            req2 = requestAPI("{0}/api/sno/satellite/{1}".format(node_code, satellite_id))

            # Get percentage
            uptime_total_count = req2["uptime"]["totalCount"]
            uptime_success_count = req2["uptime"]["successCount"]
            uptime_checks = percentage(uptime_success_count, uptime_total_count)

            audit_total_count = req2["audit"]["totalCount"]
            audit_success_count = req2["audit"]["successCount"]
            audit_checks = percentage(audit_success_count, audit_total_count)

            print("Send info satellite {0} to user {1} node {2}".format(satellite_id, infouser_db['_id'], node_code))

            message_text = "🛰️ *{0}*\n\n_Uptime Checks_: *{1}%*\n_Audit Checks_: *{2}%*\n\n{3}{4}".format(
                req["satellites"][int(n_stellite)]["url"], uptime_checks, audit_checks, statsString(req2), warning)

        except Exception as c:
            print(c)
            message_text = "*--- Other Info ---*\n\n🔴 An error occurred while getting the information, try again " \
                           "later or check your node. "

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=KeyboardOtherSatellite(node_code))

    # Callback otherinfo
    elif re.search("^otherinf-+", call.data):
        node_code = str(call.data).replace('otherinf-', '')

        print("Get {0}/api/sno/ to user: {1}".format(node_code, infouser_db['_id']))
        try:
            req = requestAPI("{0}/api/sno/".format(node_code))
            uptodate = req["upToDate"]

            if uptodate:
                uptodate = "🟢"
            else:
                uptodate = "🔴"

            version = req["version"]
            wallet = req["wallet"]
            nodeid = req["nodeID"]

            message_text = "*--- Other Info ---*\n\n*Up to Date:* {0}\n*Version:* {1}\n\n*Wallet:* `{2}`\n\n" \
                           "*Node ID:* `{3}`".format(uptodate, version, wallet, nodeid)
            print("Send Other Info to user: {0}".format(infouser_db['_id']))

        except Exception as c:
            print(c)
            message_text = "*--- Other Info ---*\n\n🔴 An error occurred while getting the information, try again " \
                           "later or check your node. "

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnCustom("stats-", node_code))

    # Callback payout
    elif re.search("^payout-+", call.data):
        node_code = str(call.data).replace('payout-', '')

        print("Get {0}/api/sno/satellites to user: {1}".format(node_code, infouser_db['_id']))
        try:
            prices = {"download": 20, "repair_audit": 10, "disk": 1.5}
            req = requestAPI("{0}/api/sno/satellites".format(node_code))

            # Calculate payout for egress Download, Repair & Audit Egress
            repair_audit_egress = 0
            download = 0
            for day in req["bandwidthDaily"]:
                repair_audit_egress = repair_audit_egress + day["egress"]["repair"] + day["egress"]["audit"]
                download = download + day["egress"]["usage"]

            e_repair_audit = convertSize(repair_audit_egress)
            payout_e_repair_audit = payments(repair_audit_egress, prices["repair_audit"], 1e12)

            e_download = convertSize(download)
            payout_e_download = payments(download, prices["download"], 1e12)

            # Calculate payout for disk average
            disk_average = convertSize(req["storageSummary"])
            payout_disk_average = payments(req["storageSummary"], prices["disk"], 1e12) / 720

            # Calculate totals
            total_disk = convertSize(req["storageSummary"]/720)
            total_bw = convertSize(download + repair_audit_egress)
            total_payouts = round(payout_e_download + payout_e_repair_audit + payout_disk_average, 2)

            m_text = "* --- Payout Estimation ---*\n\n*Download*\n• _Type:_ Engress\n• _Price:_ ${0}/TB" \
                     "\n• _Band Width:_ {1}\n• _Payout:_ ${2:.2f}" \
                     "\n\n".format(prices["download"], e_download, round(payout_e_download, 2))
            m_text = m_text + "*Repair & Audit*\n• _Type:_ Egress\n• _Price:_ ${0}/TB\n• " \
                              "_Band Width:_ {1}\n• _Payout:_ ${2:.2f}" \
                              "\n\n".format(prices["repair_audit"], e_repair_audit, round(payout_e_repair_audit, 2))
            m_text = m_text + "*Disk Average Month*\n• _Type:_ Storage\n• _Price:_ ${0}/TBm\n" \
                              "• _Disk:_ {1}h\n• _Payout:_ ${2:.2f}" \
                              "\n\n".format(prices["disk"], disk_average, round(payout_disk_average, 2))
            m_text = m_text + "*TOTAL*\n• _Disk:_ {0}m\n• _Band Width:_ {1}\n• " \
                              "*Payout: ${2:.2f}*\n".format(total_disk, total_bw, total_payouts)
            print("Send Payout Info to user: {0}".format(infouser_db['_id']))

        except Exception as c:
            print(c)
            m_text = "*--- Other Info ---*\n\n🔴 An error occurred while getting the information, try again " \
                     "later or check your node. "

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=m_text,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnCustom("stats-", node_code))

    # Callback changeport
    elif re.search("^changeport-+", call.data):
        node_code = str(call.data).replace('changeport-', '')

        users_col.update_one({"_id": str(infouser_db['_id'])}, {
            "$set": {"lastMessage.type": "changeport", "lastMessage.idMessage": str(call.message.message_id),
                     "lastMessage.text": node_code}})

        message_text = "OK, send the new Storj Port of your node to be able to check it. The entire address is not" \
                       " necessary, only the port."

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=message_text, parse_mode='Markdown')

    # Callback changedowntime
    elif re.search("^changedowntime-+", call.data):
        node_code = str(call.data).replace('changedowntime-', '')

        users_col.update_one({"_id": str(infouser_db['_id'])}, {
            "$set": {"lastMessage.type": "changedowntime", "lastMessage.idMessage": str(call.message.message_id),
                     "lastMessage.text": node_code}})

        message_text = "Ok, send the idle time that has to pass before sending the notification that the Storj node " \
                       "is unavailable."

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=message_text, parse_mode='Markdown')

    # Callback cancel contact
    elif call.data == "cancelcontact":
        users_col.update_one({"_id": str(infouser_db['_id'])}, {"$set": {"contact": False}}, upsert=True)
        print("User {0} cancel command contact".format(infouser_db['_id']))
        bot.send_message(infouser_db['_id'], main_message, parse_mode="Markdown")

    else:
        print("Callback unrecognized for user {0}".format(call.message.chat.id))


while True:
    try:
        bot.polling(none_stop=True, timeout=30)
    except Exception as e:
        print(e)
