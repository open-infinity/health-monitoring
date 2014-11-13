#!/usr/bin/env python2

import threading
import sys
import SocketServer
import json
import logging
import time
import thread

import util
import node


class UDPSocketListener(threading.Thread):
    """Implements a thread used for listening to master heartbeats."""
    # def __init__(self, a_node, a_heartbeats_received, a_master_list,
    # a_active_node_list, a_lock_resources):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('nodechecker.listener')
        self._server = None
        self.ctx = context
        #self.node = a_node
        #self.heartbeats_received = a_heartbeats_received
        #self.master_list = a_master_list
        #self.active_node_list = a_active_node_list
        #self.lock_resources = a_lock_resources

    def run(self):
        print("Thread:" + str(thread.get_ident()) + ' ' + "ENTER UDPServer.run()")

        bind_to_address = "0.0.0.0"
        self._server = SocketServer.UDPServer((bind_to_address, self.ctx.this_node.port),
                                              UDPDataHandler)
        self._server.logger = self.logger
        self._server.ctx = self.ctx
        #self._server.node = self.ctx.this_node
        #self._server.heartbeats_received = self.ctx.heartbeats_received
        #self._server.master_list = self.ctx.master_list
        #self._server.active_node_list = self.ctx.active_node_list
        #self._server.lock_resources = self.ctx.resource_lock
        self._server.serve_forever()
        print("Thread:" + str(thread.get_ident()) + ' ' + "EXIT UDPServer.run")

    def shutdown(self):
        print("Thread:" + str(thread.get_ident()) + ' ' + "ENTER UDPSocketListener.shutdown()")

        if self._server:
            self.do_shutdown()
        else:
            print("Thread:" + str(thread.get_ident()) + ' ' + "Waiting for server...")
            time.sleep(5)
            self.do_shutdown()

        #while not self._server:
        #    print("Waiting for server...")
        #    time.sleep(1)
        #print("UDPServer about to shut down")
        #self._server.shutdown()
        #self._server = None
        #print("UDPServer is None")

        #if self._server:
        #    print("UDPServer about to shut down")
        #    self._server.shutdown()
        #    self._server = None
        #    print("UDPServer is None")
        print("Thread:" + str(thread.get_ident()) + ' ' + "EXIT UDPSocketListener.shutdown()")

    def do_shutdown(self):
        print("Thread:" + str(thread.get_ident()) + ' ' + "ENTER UDPSocketListener.do_shutdown()")
        self._server.shutdown()
        self._server = None
        print("Thread:" + str(thread.get_ident()) + ' ' + "EXIT UDPSocketListener.do_shutdown()")


class UDPDataHandler(SocketServer.BaseRequestHandler):
    """Handles data received by a heartbeat signal
       Note accessing of UDPSocketListener internal variables
       through server object, e.g. self.server.active_node_list
    """

    def handle(self):
        self.server.ctx.resource_lock.acquire()
        try:
            data = self.request[0].strip()
            json_object = json.loads(data)

            # Received heartbeat signal
            if json_object[0] == "node":
                self.handle_heartbeat(json_object)

            # Received active_node_list. Should be sent only to slaves
            elif json_object[0] == "active_node_list" and self._server.ctx.this_node.role == "SLAVE":
                print("recv act nl")
                self.handle_list(json_object)

            else:
                print("unexp")
                self._server.logger.warn("Received unexpected data")
        except (TypeError, RuntimeError):
            util.log_exception(sys.exc_info())
        finally:
            self.server.ctx.resource_lock.release()

    def handle_heartbeat(self, json_object):
        print ("ENTER handle_heartbeat")
        self.server.logger.debug("Received Heartbeat")
        tx_node = node.Node().from_dict(json_object[1])
        if tx_node != self.server.ctx.this_node:
            print("2")
            self.server.ctx.heartbeats_received += 1
            if tx_node not in self.server.ctx.master_list:
                self.server.ctx.master_list.append(tx_node)
                self.server.logger.debug("Added a master to the master_list")
            self.server.logger.debug("Received master %s, master list is having size:%d" %
                                     (tx_node.hostname, len(self.server.ctx.master_list)))
            for m in self.server.ctx.master_list:
                self.server.logger.debug("name = %s" % m.hostname)
        else:
            print("3")
            self.server.logger.debug("Received heartbeat from myself")

    def handle_active_node_list(self, json_object):
        self.server.logger.debug("Received new active_node_list")
        self.server.ctx.active_node_list[:] = node.node_list_from_dict_list(json_object[1])
        self.server.logger.debug("New active list is ")
        self.server.logger.debug(self._server.ctx.active_node_list)
