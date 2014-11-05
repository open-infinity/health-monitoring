#!/usr/bin/env python2

import threading
import sys
import SocketServer
import json
import logging
import util
import node


class UDPSocketListener(threading.Thread):
    """Implements a thread used for listening to master heartbeats."""
    def __init__(self, a_node, a_heartbeats_received, a_master_list,
                 a_active_node_list, a_lock_resources):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('nodechecker.listener')
        self.__server = None
        self.node = a_node
        self.heartbeats_received = a_heartbeats_received
        self.master_list = a_master_list
        self.active_node_list = a_active_node_list
        self.lock_resources = a_lock_resources

    def run(self):
        bind_address = "0.0.0.0"
        self.__server = SocketServer.UDPServer((bind_address, self.node.port),
                                               UDPDataHandler)

        self.__server.logger = self.logger
        self.__server.node = self.node
        self.__server.heartbeats_received = self.heartbeats_received
        self.__server.master_list = self.master_list
        self.__server.active_node_list = self.active_node_list
        self.__server.lock_resources = self.lock_resources
        self.__server.serve_forever()

    def shutdown(self):
        if self.__server:
            self.__server.shutdown()
            self.__server = None


class UDPDataHandler(SocketServer.BaseRequestHandler):
    """Handles data received by a heartbeat signal
       Note accessing of UDPSocketListener internal variables
       through server object, e.g. self.server.active_node_list
    """

    def handle(self):
        self.server.lock_resources.acquire()
        try:
            data = self.request[0].strip()
            json_object = json.loads(data)

            # Received heartbeat signal
            if json_object[0] == "node":
                self.server.logger.debug("Received Heartbeat")
                recv_node = node.Node().from_dict(json_object[1])
                if recv_node != self.server.node:
                    self.server.heartbeats_received += 1
                    if recv_node not in self.server.master_list:
                        self.server.master_list.append(recv_node)
                        self.server.logger.debug(
                            "Added a master to the master_list")
                    self.server.logger.debug(
                          "Received master %s, master list is having size:%d" %
                          (recv_node.hostname, len(self.server.master_list)))
                    for m in self.server.master_list:
                        self.server.logger.debug("name = %s" % m.hostname)
                else:
                    self.server.logger.debug("Received heartbeat from myself")

            # Received active_node_list. Should be sent only to slaves
            elif json_object[0] == "active_node_list" \
                                    and self.server.node.role == "SLAVE":
                self.server.logger.debug("Received new active_node_list")
                self.server.active_node_list[:] = node.\
                                                  node_list_from_dict_list(
                                                  json_object[1])
                self.server.logger.debug("New active list is ")
                self.server.logger.debug(self.server.active_node_list)
            else:
                self.server.logger.warn("Received unexpected data")
        except (TypeError, RuntimeError):
            util.log_exception(sys.exc_info())
        finally:
            self.server.lock_resources.release()
