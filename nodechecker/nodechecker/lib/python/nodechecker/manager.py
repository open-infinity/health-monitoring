#!/usr/bin/env python2

#
# Desc
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility
import logging
import sys
import threading
import time

import timer
import util
import udp_listener


class Manager(threading.Thread):
    def __init__(self, a_context):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger('nodechecker.loop')
        self._ctx = a_context
        self._continue = True
        self._udp_listener = udp_listener.UDPSocketListener(self._ctx)
        self._hb_sender = timer.HeartBeatSender(self._ctx.heartbeat_period,
                                                [self._ctx])

        self._dead_node_scanner = timer.DeadNodeScanner(self._ctx)

    def run(self):
        self._continue = True
        self._udp_listener.start()
        self._loop_forever()
        # print("Thread:" + str(thread.get_ident()) + ' ' + 'EXIT Manager.run() ')

    def shutdown(self):
        self._continue = False
        self._stop_workers()

    def _loop_forever(self):
        index = 0
        while self._continue:
            index = self._master_election(index)

        # print("Thread:" + str(thread.get_ident()) + ' ' + 'EXIT Manager._loop_forever() ')
    '''
    def _do_shutdown(self, exc_info=None, exit_status=1, message="Shutting down"):
        self._stop_workers()
        util.log_message(message, exc_info)
        #print("Shutting down " + str(exc_info))
    '''
    def _stop_workers(self):
        print("ENTER _stop_workers")
        if self._hb_sender.isAlive():
            self._hb_sender.cancel()
            self._hb_sender.join()

        if self._udp_listener.isAlive():
            self._udp_listener.shutdown()
            self._udp_listener.join()

        if self._dead_node_scanner.isAlive():
            self._dead_node_scanner.cancel()
            self._dead_node_scanner.join()

    def _master_election(self, index):
        print('_master_election ENTER')
        new_index = index
        try:
            my_pos = self._ctx.active_node_list.index(self._ctx.this_node)
            print("_master_election My position in the list:" + str(my_pos) + " index:" + str(index))

            # logger.debug("My position in the list is %d, a = %d" % (my_pos, index))
            count = self._get_master_count()

            # In case that master has changed, assign a new master to self
            if self._ctx.this_node.role == "SLAVE" and self._ctx.master_list:
                if self._ctx.my_master not in self._ctx.master_list:
                    self._assign_master(self._ctx.master_list[0])

            # If there is not enough of masters, and own ranking on the list
            # equals index, then become master
            if count == "TOO_LOW":
                print ("too low")
                if index == my_pos:
                    print("'_master_election _become_a_master")
                    self._become_a_master()
                new_index = (index + 1) % len(self._ctx.active_node_list)
                print("index:" + str(index))

            # In case that there is enough or too many masters, become
            # slave
            else:
                self._become_a_slave()

        except:
            print("_master_election - shutdown " + str(sys.exc_info()))
            util.log_message("Shutting down", sys.exc_info())
            self.shutdown()

        return new_index

    def _get_master_count(self, heartbeat_periods=1):
        """Listens to master heartbeat signals.
        Depending on of number of received signals, a decision is made on
        how to proceed:
            - In case of too small number of signals, the node attempts to be
            itself a master.
            - In case of too big number of signals, if the node is a slave, it
            checks if it should itself run as a slave.
        """
        print("_get_master_count ENTER")

        ret = "FINE"
        self._ctx.heartbeats_received = 0
        self._ctx.master_list[:] = []

        # Sleep, count masters when awake, then all your base are belong to us.
        print("_get_master_count sleep")
        time.sleep(heartbeat_periods * self._ctx.heartbeat_period)
        print("_get_master_count awake")
        print("_get_master_count role: " + self._ctx.this_node.role)

        self._ctx.resource_lock.acquire()
        try:
            if self._ctx.this_node.role == "MASTER":
                expected_masters = 0
            else:
                expected_masters = 1

            if len(self._ctx.master_list) < expected_masters:
                ret = "TOO_LOW"
            elif len(self._ctx.master_list) > expected_masters:
                ret = "TOO_HIGH"
            else:
                ret = "FINE"

                #if self._ctx.this_node.role == "SLAVE" and self._ctx.master_list:
                #    if self._ctx.my_master not in self._ctx.master_list:
                #        self.assign_master(self._ctx.master_list[0])

        except:
            print("_get_master_count exception: " + sys.exc_info())
            util.log_exception(sys.exc_info())
        finally:
            self._ctx.resource_lock.release()
        print("_get_master_count EXIT returning " + str(ret))
        return ret

    def _assign_master(self, new_master):
        # global my_master, node_manager
        self._logger.info("Configuring node name %s as a SLAVE, master name is %s"
                          % (self._ctx.this_node.hostname, new_master.hostname))
        self._ctx.my_master = new_master
        self._ctx.node_manager.configure_node_as_slave(
            self._ctx.this_node.ip_address, self._ctx.RRD_HTTP_SERVER_PORT,
            self._ctx.my_master.ip_address,
            self._ctx.RRD_HTTP_SERVER_PORT)

    def _become_a_master(self):
        """Triggers actions needed to prepare the node for running
        in MASTER role. Runs the master loop.
        """
        # global Thread, node_manager

        print("_become_a_master,ENTER  role: " + self._ctx.this_node.role)
        if self._ctx.this_node.role != "MASTER":
            self._ctx.this_node.role = "MASTER"
            self._logger.info("This node became a MASTER")
            print("_become_a_master() starting _dead_node_scanner")
            self._dead_node_scanner.start()
            print("_become_a_master() starting _hb_sender")
            self._hb_sender.start()
            print("_become_a_master() configure_node_as_master")

            self._ctx.node_manager.configure_node_as_master(self._ctx.this_node.ip_address)
            print("_become_a_master store_list_to_file")
            
            # master nodes use active_node_list file
            util.store_list_to_file(self._ctx.active_node_list, self._ctx.active_node_list_file,
                                    self._ctx.this_node.group_name)
            print("_become_a_master exiting if")
        else:
            print("*******role is  MASTER")
        print("_become_a_master _master_loop")
        self._master_loop()
        print("_become_a_master EXIT")
        print(self._ctx.this_node.role)

    def _become_a_slave(self):
        self._logger.info("Trying to become a SLAVE")

        if self._ctx.this_node.role == "MASTER":
            self._stop_workers()
            self._ctx.this_node.role = "SLAVE"
            if self._ctx.master_list:
                self._assign_master(self._ctx.master_list[0])
            else:
                util.log_message("Unable to set a master for the node, master list empty", sys.exc_info())
                self.shutdown()

        self._slave_loop(self._ctx.node_list)

    def _continue_as_master(self):
        """Returns True if a node should continue in master role"""
        try:
            ret = True
            my_pos = self._ctx.active_node_list.index(self._ctx.this_node)
            for m in self._ctx.master_list:
                master_pos = self._ctx.active_node_list.index(m)
                if master_pos < my_pos:
                    ret = False
                    break
            self._logger.info("Continuing as master: %s" % str(ret))
        except ValueError:
            self._logger.debug("Active node list: %s" % self._ctx.active_node_list)
            self._logger.debug("Master list: %s" % self._ctx.master_list)
            self._logger.debug("Master: %s" % m)
            util.log_exception(sys.exc_info())
            print("_continue_as_master" + sys.exc_info())
        return ret

    def _master_loop(self):
        # global node_list
        # global active_node_list
        #global dead_node_set
        print("_master_loop ENTER")
        self._logger.info("Master Loop start")

        while self._continue:
            print("_master_loop while loop start")

            # 1) Check number of masters
            if self._get_master_count(1) == "TOO_HIGH":
                if not self._continue_as_master():
                    break

            # 2) Read node list file, update own node collections if needed
            self._ctx.resource_lock.acquire()
            print("_master_loop _sync_collections")
            node_list_changed = self._sync_collections(self._ctx.node_list)[0]

            # 3) Process notifications
            #mail_sender.send_notifications(ntf_reader.get_notifications(node_list))
            self._ctx.ntf_manager.process_notifications(self._ctx.ntf_reader.get_notifications(self._ctx.node_list))

            # 4) Send and store changes
            if node_list_changed:
                util.send(self._ctx.this_node,
                          self._ctx.active_node_list,
                          util.json_from_list(self._ctx.active_node_list, 'active_node_list'))
                util.store_list_to_file(self._ctx.active_node_list, self._ctx.active_node_list_file,
                                        self._ctx.this_node.group_name)
            # 5) release lock
            self._ctx.resource_lock.release()

        # Can not continue as master
        if self._continue: self._become_a_slave()

    def _slave_loop(self, a_node_list):
        self._logger.info("Slave Loop start")
        while self._continue:
            try:
                self._sync_collections(a_node_list)
                if self._get_master_count(2) == "TOO_LOW":
                    break
            except:
                self.shutdown()
                util.log_exception(sys.exc_info())

    # TODO who calls this?
    def _wait_for_machine_configured(self, file_reader):
        """In case of nosql and bigdata CMT is changing hostname, wait for that
           action being complete"""

        total_sleep_time = 0
        wait_for_conf = False
        for n in self._ctx.node_list:
            machine_type = file_reader.read_attribute(n.ip_address, 'MACHINE_TYPE')
            if machine_type == 'manager':
                wait_for_conf = True
                break
        if wait_for_conf:
            while True:
                if util.get_hostname() != self._ctx.this_node.hostname:
                    self._logger.debug("Sleep")
                    total_sleep_time += self._ctx.CMT_CONF_WAIT
                    if total_sleep_time >= self._ctx.MAX_CMT_CONF_WAIT:
                        util.log_exception("Waiting for machine configurtion took too long")
                        self.shutdown()
                    time.sleep(self._ctx.CMT_CONF_WAIT)
                else:
                    # sleep once more before the exit: to make sure that hostname
                    # change propagated
                    time.sleep(self._ctx.CMT_CONF_WAIT)
                    break

    ''' 
    Update active_node_list based on freshly read nodelist.conf file.
    That file is updated by admin or puppet master, which know what nodes
    should be in the cluster
    
    Returns freshly read node_list and the flag if active noode list changed
    '''
    def _sync_collections(self, a_node_list):
        """Read a_node_list, and update active_node_list and dead_node_list,
        if needed"""

        try:
            a_node_list[:] = self._ctx.nodelist_reader.read_node_list(self._ctx.this_node, self._ctx.mode)

            # Check if cluster scaled out, or just created
            # Fetch new nodes and add them to active_node_list
            nodes = [n for n in a_node_list if n not in self._ctx.active_node_list and
                     n.ip_address not in self._ctx.dead_node_set]
            for m in nodes:
                self._ctx.active_node_list.append(m)
            if nodes:
                active_nodes_changed = True
            else:
                active_nodes_changed = False

            # Check if cluster scaled in
            # Remove node from active_node_list, if the node is not present any more
            # in the cluster
            nodes = [n for n in self._ctx.active_node_list if n not in a_node_list]
            for m in nodes:
                self._ctx.active_node_list.remove(m)
            if nodes:
                active_nodes_changed = True
            
            # Remove node from dead_node_set, if the node if the node is not present any more
            # in the cluster
            nodes = [ip for ip in self._ctx.dead_node_set
                     if not util.find_node_by_ip(ip, a_node_list)]
            for m in nodes:
                self._ctx.dead_node_set.remove(m)
                
        except ValueError:
            util.log_exception(sys.exc_info())

        return active_nodes_changed, a_node_list

    # TODO: who should use this?
    def _set_master(self):
        if not self._ctx.node_list:
            util.log_exception(sys.exc_info(), "Unable to set a master for the node")
            self.shutdown()
        self._assign_master(self._ctx.node_list[0])



