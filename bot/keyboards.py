from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Keyboard to list address
def keyboardNodes(nodes, prefix, button_return=True):
    # We get number of nodes and if it's even or odd
    i = nodes.count()
    modI = i % 2

    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    if i == 1:
        markup.add(InlineKeyboardButton(nodes[0]['name'], callback_data=prefix + nodes[0]['address']))

    else:
        # If it's odd
        if modI == 1:
            k = 0
            for j in range(int((i - 1) / 2)):
                markup.add(InlineKeyboardButton(nodes[k]['name'], callback_data=prefix + nodes[k]['address']),
                           InlineKeyboardButton(nodes[k + 1]['name'],
                                                callback_data=prefix + nodes[k + 1]['address']))

                k = k + 2

            markup.add(
                InlineKeyboardButton(nodes[k]['name'], callback_data=prefix + nodes[k]['address']))

        # If it's even
        else:
            k = 0
            for j in range(int(i / 2)):
                markup.add(InlineKeyboardButton(nodes[k]['name'], callback_data=prefix + nodes[k]['address']),
                           InlineKeyboardButton(nodes[k + 1]['name'],
                                                callback_data=prefix + nodes[k + 1]['address']))

                k = k + 2

    # Button to return
    if button_return:
        markup.add(
            InlineKeyboardButton("« Return", callback_data="statsReturn"))

    return markup


# Keyboard with options for address (edit, delete, view...)
def keyboardOptionsNode(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("View Stats", callback_data="stats-" + node_code),
        InlineKeyboardButton("Edit Node", callback_data="editNode-" + node_code),
        InlineKeyboardButton("Delete Node", callback_data="delNode-" + node_code),
        InlineKeyboardButton("Notifications", callback_data="notNode-" + node_code),
        InlineKeyboardButton("« Return", callback_data="myNodes"))

    return markup


# Keyboard edit configuracion node (name, code)
def keyboardEditNode(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Edit name", callback_data="setNodeName-" + node_code),
        InlineKeyboardButton("Edit address", callback_data="setNodeAddr-" + node_code))

    return markup


# Keybpard return Node or Nodes List
def keyboardReturn(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("« Back to Node", callback_data="mynode-" + node_code),
        InlineKeyboardButton("« Back to Nodes List", callback_data="myNodes"))

    return markup


# Keyboard confirm delete node
def keyboardDeleteNode(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Yes, delete the Node",
                             callback_data="yesDelNode-" + node_code),
        InlineKeyboardButton("No", callback_data="myNodes"))

    return markup


# Keyboard to return select stats for myNodes
def keyboardReturnMyNodes():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("« Back to Nodes List", callback_data="myNodes"))

    return markup


# Keyboard notifications
def keyboardNotifications(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("ON", callback_data="notON-" + node_code),
        InlineKeyboardButton("OFF", callback_data="notOFF-" + node_code),
        InlineKeyboardButton("Change Port", callback_data="changeport-" + node_code),
        InlineKeyboardButton("Change Downtime", callback_data="changedowntime-" + node_code)
    )

    return markup


# Keyboard nodeinfo
def keyboardNodeInfo(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Utilization & Remaning", callback_data="utilization-" + node_code),
        InlineKeyboardButton("Payout", callback_data="payout-" + node_code),
        InlineKeyboardButton("Other Info", callback_data="otherinf-" + node_code),
        InlineKeyboardButton("« Back to Nodes List", callback_data="myNodes"))

    return markup


# Keyboard return to last keyboard
def keyboardReturnCustom(prefix, node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("« Return", callback_data=prefix + node_code))

    return markup


# Keyboard return to node info o satellites
def keyboardNodeInfoSatellites(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("« Return", callback_data="stats-" + node_code),
        InlineKeyboardButton("Satellites", callback_data="satellites-" + node_code),
        InlineKeyboardButton("Uptime & Audits", callback_data="uptimeaudits-" + node_code))
    return markup


# Keyboard list satellites
def keyboardSatellites(node_code, req):
    list_satellites = req["satellites"]
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    i = 0
    for satellite in list_satellites:

        if satellite["disqualified"] is not None or satellite["suspended"] is not None:
            markup.add(InlineKeyboardButton("⚠ " + satellite["url"], callback_data="sat-{0}#{1}".format(node_code, i)))

        else:
            markup.add(InlineKeyboardButton(satellite["url"], callback_data="sat-{0}#{1}".format(node_code, i)))

        i = i + 1

    return markup


# Keyboard select other satellite
def KeyboardOtherSatellite(node_code):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("« Node Info", callback_data="stats-" + node_code),
        InlineKeyboardButton("« Return", callback_data="satellites-" + node_code))

    return markup

# Keyboard cancell command contact
def keyboardCancelContact():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("« Return", callback_data="cancelcontact"))

    return markup
