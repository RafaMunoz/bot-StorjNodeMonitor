import urllib3
import json
import sys
import os
import math
from datetime import datetime

# Objeto HTTP
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()


# Check environment variable
def checkEnviron(env):
    try:
        return os.environ[env]
    except KeyError:
        print("Please set the environment variable {0}".format(env))
        sys.exit(1)


# Request to API data
def requestAPI(argurl):
    try:
        response = http.request('GET', url=argurl)
        if response.status != 200:
            data_json = {"ok": False, "error_code": response.status, "description": response.data.decode('utf-8')}
        else:
            data_json = json.loads(response.data.decode('utf-8'))
        return data_json

    except Exception as e2:
        data_json = {"ok": False, "description": str(e2)}
        return data_json


# Convert bytes to MB -> GB -> TB
def convertSize(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1000)))
    power = math.pow(1000, i)
    size = round(size_bytes / power, 2)
    return "{} {}".format(size, size_name[i])


# Convert time to pretty string
def pretty_date(time_obj):
    second_diff = time_obj.seconds
    day_diff = time_obj.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "Just Now"
        if second_diff < 60:
            return "{0} seconds ago".format(int(second_diff))
        if second_diff < 120:
            return "1 minute ago"
        if second_diff < 3600:
            return "{0} minutes ago".format(int(second_diff / 60))
        if second_diff < 7200:
            return "1 hour ago"
        if second_diff < 86400:
            return "{0} hours ago".format(int(second_diff / 3600))
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return "{0} days ago".format(day_diff)
    if day_diff < 31:
        return "{0} weeks ago".format(int(day_diff / 7))
    if day_diff < 365:
        return "{0} months ago".format(int(day_diff / 30))
    return " years ago".format(int(day_diff / 365))


# Return string with the statistics month and today
def statsString(data):
    # This month
    storage_summary = convertSize(data["storageSummary"])
    band_width_summary = convertSize(data["bandwidthSummary"])
    egress_summary = convertSize(data["egressSummary"])
    ingress_summary = convertSize(data["ingressSummary"])

    # Today
    storage_today = data["storageDaily"][len(data["storageDaily"]) - 1]
    disk_today = convertSize(storage_today["atRestTotal"])
    date_today = datetime.strftime(datetime.strptime(storage_today["intervalStart"], "%Y-%m-%dT%H:%M:%SZ"),
                                   "%a, %d %B %Y")

    # egress & ingress today
    bandwidth_daily = data["bandwidthDaily"][len(data["bandwidthDaily"]) - 1]
    en_audit = convertSize(bandwidth_daily["egress"]["audit"])
    en_repair = convertSize(bandwidth_daily["egress"]["repair"])
    en_usage = convertSize(bandwidth_daily["egress"]["usage"])
    in_repair = convertSize(bandwidth_daily["ingress"]["repair"])
    in_usage = convertSize(bandwidth_daily["ingress"]["usage"])

    message_text = "*This month*\n- _Disk Space use:_ {0}h\n- _Band Width use:_ {1}\n• _Egress:_ {2}\n• _Ingress:_ " \
                   "{3}\n\n".format(storage_summary, band_width_summary, egress_summary, ingress_summary)
    message_text = message_text + "*{0}*\n- _Disk Space use:_ {1}h\n\n- Egress:\n• _Usage:_ {2}\n• _Repair:_ {3}\n• " \
                                  "_Audit:_ {4}\n\n".format(date_today, disk_today, en_usage, en_repair, en_audit)
    message_text = message_text + "- Ingress:\n• _Usage:_ {0}\n• _Repair:_ {1}".format(in_usage, in_repair)

    return message_text


# Return percentage
def percentage(c, a):
    result = (c * 100) / a

    return round(result, 2)


# Return Payment
def payments(consumed, price, bytes_price):
    result = (consumed * price) / bytes_price

    return result


# Convert string date with nanoseconds
def convertDate(date_string):
    date_split = date_string.split(".")
    date = "{0}.{1}Z".format(date_split[0], (date_split[1])[:6])
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
