#!/usr/bin/env python2

import json
import commands
import logging
import sys
import traceback
import socket

logger = logging.getLogger('nodechecker.util')


def log_message(message, exc_info):
    logger.error("%s" % message)
    if exc_info:
        log_exception(exc_info)


def log_exception(exc_info):
    logger.error(repr(traceback.format_exception(exc_info[0], exc_info[1],
                                                 exc_info[2])))


def find_node_by_ip(ip, node_list):
    for n in node_list:
        if ip == n.ip_address:
            return True
    return False


def json_from_list(a_node_list, title):
    """ Returns json document with a list formated like:
    ["title", [{node1 dict},{node2 dict}] ]
    where node1, node2, .. are members of a_node_list
    """
    data = [title]
    list_of_node_dicts = []
    for n in a_node_list:
        list_of_node_dicts.append(n.to_dict())
    data.append(list_of_node_dicts)
    json_dump = json.dumps(data)
    return json_dump


def get_ip_address():
    return commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]


def get_hostname():
    return commands.getoutput("/bin/hostname")


def store_list_to_file(a_list, a_file, group_name):
    try:
        with open(a_file, 'w') as f:
            for n in a_list:
                f.write("".join([n.ip_address, " ",
                                 n.ip_address_public, " ",
                                 n.hostname, " ",
                                 n.machine_type, " ",
                                 n.machine_id, " ",
                                 group_name, "\n"]))
            f.flush()
    except:
        log_message("Error processing file %s" % a_file, sys.exc_info())


def send(this_node, to_nodes, data):
    # def send(ctx):
    print("ENTER send()")
    try:
        if len(to_nodes) > 0:
            # _#logger.debug("Sending data %s" % str(data))
            print("Sending data:" + str(data))

            for n in to_nodes:
                if n != this_node:
                    # _#logger.debug("Sending to node %s" % str(n.ip_address))
                    print("Sending to node:" + str(n.ip_address))
                    print("Sending to port:" + str(n.port))

                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(data, (n.ip_address, n.port))
        else:
            # _do_shutdown()(None, 1, "No nodes to send data")
            pass
            print("nodes not here")
    except:
        print("EXCEPTION in send() " + sys.exc_info())
        log_exception(sys.exc_info())
