#!/usr/bin/env python2

#
# Desc
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility
import logging

import sys
import os
import subprocess
import signal
import socket
import threading
import time
import config
import notification.parser
import notification.manager
import functools
import reader
import util
import node
import thread
import udp_listener


class Worker(threading.Thread):
    def __init__(self, a_context):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger('nodechecker.loop')
        self._ctx = a_context
        self._continue = True
        self._udp_listener = udp_listener.UDPSocketListener(self._ctx)
        # self._udp_listener = udp_listener.UDPSocketListener(this_node,
        #                                                     heartbeats_received,
        #                                                    master_list,
        #                                                     active_node_list,
        #                                                     lock_resources)

    def run(self):
        self._udp_listener.start()
        self._loop_forever()
        # print("Thread:" + str(thread.get_ident()) + ' ' + 'EXIT Worker.run() ')

    def shutdown(self):
        self._continue = False

    def _loop_forever(self):
        index = 0
        while self._continue:
            index = self._master_election(index)

        self._do_shutdown()
        # print("Thread:" + str(thread.get_ident()) + ' ' + 'EXIT Worker._loop_forever() ')

    def _do_shutdown(self, exc_info=None, exit_status=1, message="Shutting down"):
        # print("Thread:" + str(thread.get_ident()) + ' ' + 'ENTER Worker._do_shutdown()')
        #def shutdown(exc_info=None, exit_status=1, message="Shutting down"):
        #nodechecker.util.log_message(message, exc_info)
        self._udp_listener.shutdown()
        # TODO: WARNING, the function moved
        self._cancel_timers()
        #sys.exit(exit_status)
        self._udp_listener.join()
        #print("Thread:" + str(thread.get_ident()) + ' ' + 'EXIT Worker._do_shutdown()')

    def _become_a_slave(self):
        pass

    def _become_a_master(self):
        pass

    #def _listen_to_master_heartbeats(self, arg):
    #    pass

    def _cancel_timers(self):
        pass

    def _master_election(self, index):
        print('ENTER master_election()')
        new_index = index
        try:
            my_pos = self._ctx.active_node_list.index(
                self._ctx.this_node)
            # print("My position in the list:" + str(my_pos) + " index:" + str(index))

            #logger.debug("My position in the list is %d, a = %d" % (my_pos, index))
            count = self._get_master_count()

            # In case that master has changed, assign a new master to self
            if self._ctx.this_node.role == "SLAVE" and self._ctx.master_list:
                if self._ctx.my_master not in self._ctx.master_list:
                    self.assign_master(self._ctx.master_list[0])

            # If there is not enough of masters, and own ranking on the list
            # equals index, then become master
            if count == "TOO_LOW":
                #print ("too low")
                if index == my_pos:
                    #print("becme master")
                    self._become_a_master()
                new_index = (index + 1) % len(self._ctx.active_node_list)
                #print("index:" + str(index))

            # In case that there is enough or too many masters, become
            # slave
            else:
                #print("bcme slave")
                self._become_a_slave()



        except:
            self._do_shutdown(sys.exc_info)
        return new_index

    def _get_master_count(self, number_of_heartbeat_periods=1):
        """Listens to master heartbeat signals.
        Depending on of number of received signals, a decision is made on
        how to proceed:
            - In case of too small number of signals, the node attempts to be
            itself a master.
            - In case of too big number of signals, if the node is a slave, it
            checks if it should itself run as a slave.
        """
        #global heartbeats_received
        #global master_list

        ret = "FINE"
        self._ctx.heartbeats_received = 0
        self._ctx.master_list[:] = []

        # Sleep, count masters when awake, then all your base are belong to us.
        time.sleep(number_of_heartbeat_periods * self._ctx.heartbeat_period)
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
            util.log_exception(sys.exc_info())
        finally:
            self._ctx.resource_lock.release()
        return ret

    def assign_master(self, new_master):
        #global my_master, node_manager
        self._logger.info("Configuring node name %s as a SLAVE, master name is %s"
                          % (self._ctx.this_node.hostname, new_master.hostname))
        self._ctx.my_master = new_master
        self._ctx.node_manager.configure_node_as_slave(
            self._ctx.this_node.ip_address, self._ctx.RRD_HTTP_SERVER_PORT,
            self._ctx.my_master.ip_address,
            self._ctx.RRD_HTTP_SERVER_PORT)


'''
    # HM Node Checker algorithm functions


    def become_a_master(self):
        """Triggers actions needed to prepare the node for running
        in MASTER role. Runs the master loop.
        """
        global delayed_dead_node_timer, node_manager

        if this_node.role != "MASTER":
            this_node.role = "MASTER"
            logger.info("This node became a MASTER")
            delayed_dead_node_timer = threading.Timer(dead_node_timeout,
                                                      start_dead_node_scan_timer)
            delayed_dead_node_timer.start()
            send_heartbeats()
            node_manager.configure_node_as_master(this_node.ip_address)
            util.store_list_to_file(active_node_list, active_node_list_file,
                                    this_node.group_name)
        master_loop()


    def become_a_slave(self):
        global this_node
        global node_list
        logger.info("Trying to become a SLAVE")
        if this_node.role == "MASTER":
            cancel_timers()
            this_node.role = "SLAVE"
            if master_list:
                assign_master(master_list[0])
            else:
                shutdown(None, 1, "Unable to set a master for the node")
        slave_loop(node_list)


    def continue_as_master(self):
        """Returns True if a node should continue in master role"""
        try:
            ret = True
            my_pos = active_node_list.index(this_node)
            for m in master_list:
                master_pos = active_node_list.index(m)
                if master_pos < my_pos:
                    ret = False
                    break
            logger.info("Continuing as master: %s" % str(ret))
        except ValueError:
            logger.debug("Active node list: %s" % active_node_list)
            logger.debug("Master list: %s" % master_list)
            logger.debug("Master: %s" % m)
            util.log_exception(sys.exc_info())
        return ret





    def master_loop(self):
        global node_list
        global active_node_list
        global dead_node_set
        logger.info("Master Loop start")
        while True:
            # 1) Check number of masters
            if listen_to_master_heartbeats(1) == "TOO_HIGH":
                if not continue_as_master():
                    break

            # 2) Read node list file, update own node collections if needed
            lock_resources.acquire()
            node_list_changed = update_node_collections(node_list)[0]

            # 3) Process notifications
            #mail_sender.send_notifications(ntf_reader.get_notifications(node_list))
            ntf_manager.process_notifications(ntf_reader.get_notifications(node_list))

            # 4) Send and store changes
            if node_list_changed:
                send(active_node_list, util.json_from_list(active_node_list,
                                                           'active_node_list'))
                util.store_list_to_file(active_node_list, active_node_list_file,
                                        this_node.group_name)
            # 5) release lock
            lock_resources.release()

        # Can not continue as master
        become_a_slave()


    def slave_loop(self, a_node_list):
        logger.info("Slave Loop start")
        while True:
            try:
                update_node_collections(a_node_list)
                if listen_to_master_heartbeats(2) == "TOO_LOW":
                    break
            except:
                shutdown(sys.exc_info())


    def wait_for_machine_configured(self, file_reader):
        """In case of nosql and bigdata CMT is changing hostname, wait for that
           action being complete"""

        total_sleep_time = 0
        wait_for_conf = False
        for n in node_list:
            machine_type = file_reader.get_attribute(n.ip_address, 'MACHINE_TYPE')
            if machine_type == 'manager':
                wait_for_conf = True
                break
        if wait_for_conf:
            while True:
                if util.get_hostname() != this_node.hostname:
                    logger.debug("Sleep")
                    total_sleep_time += CMT_CONF_WAIT
                    if total_sleep_time >= MAX_CMT_CONF_WAIT:
                        shutdown(None, 1, "This is boring, bye.")
                    time.sleep(CMT_CONF_WAIT)
                else:
                    # sleep once more before the exit: to make sure that hostname
                    # change propagated
                    time.sleep(CMT_CONF_WAIT)
                    break
    # HM Nodechecker feature functions
    def send(self, to_nodes, data):
        try:
            if len(to_nodes) > 0:
                logger.debug("Sending data %s" % str(data))
                for n in to_nodes:
                    if n != this_node:
                        logger.debug("Sending to node %s" % str(n.ip_address))
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(data, (n.ip_address, n.port))
            else:
                shutdown(None, 1, "No nodes to send data")
        except:
            util.log_exception(sys.exc_info())


    def send_heartbeats(self):
        global heartbeat_timer
        lock_resources.acquire()
        try:
            send(node_list, this_node.to_json())
            heartbeat_timer = threading.Timer(heartbeat_period, send_heartbeats)
            heartbeat_timer.start()
        except:
            util.log_exception(sys.exc_info())
        finally:
            lock_resources.release()


    def start_dead_node_scan_timer(self):
        global dead_node_timer
        dead_node_scan()
        dead_node_timer = threading.Timer(
            rrd_scan_period, start_dead_node_scan_timer)
        dead_node_timer.start()


    def cancel_timers(self):
        global heartbeat_timer
        global dead_node_timer
        global delayed_dead_node_timer

        if heartbeat_timer:
            heartbeat_timer.cancel()
        if dead_node_timer:
            dead_node_timer.cancel()
        if delayed_dead_node_timer:
            delayed_dead_node_timer.cancel()


    def find_minimal_rrd_timestamp(self, arg, dirname, names):
        global min_time_diff
        for name in names:
            filename = os.path.join(dirname, name)
            if os.path.isfile(filename):
                pipe = subprocess.Popen(
                    ['rrdtool', 'last', filename], stdout=subprocess.PIPE)
                out = pipe.communicate()
                epoch = int(out[0])
                if epoch > 0:
                    diff = arg - epoch
                    if min_time_diff > diff:
                        min_time_diff = diff
                else:
                    pass


    def check_node_still_dead(self, node_to_check):
        global active_node_list
        global new_dead_node_set
        global dead_node_set
        global min_time_diff

        now = time.mktime(time.localtime())
        path = os.path.join(conf.collectd_home, conf.collectd_rrd_dir,
                            node_to_check.hostname)
        lock_resources.acquire()
        try:
            min_time_diff = BIG_TIME_DIFF
            os.path.walk(path, find_minimal_rrd_timestamp, now)
            diff = min_time_diff
            if diff < dead_node_timeout:
                pass
            else:
                active_node_list.remove(node_to_check)
                dead_node_set.add(node_to_check.ip_address)
                send(node_list, util.json_from_list(
                    active_node_list, 'active_node_list'))
                ntf_manager.process_node_status_alerts([node_to_check], "DEAD_NODE")
                util.store_list_to_file(
                    active_node_list, active_node_list_file, this_node.group_name)
            new_dead_node_set.remove(node_to_check.ip_address)
        except:
            util.log_exception(sys.exc_info())
        finally:
            lock_resources.release()


    def process_node_resurrection(self, resurrected_node, active_nodes, dead_nodes):
        if resurrected_node in node_list:
            active_nodes.append(resurrected_node)
            dead_nodes.remove(resurrected_node.ip_address)
            return True
        else:
            return False


    def dead_node_scan(self):
        global min_time_diff
        global new_dead_node_set
        global delayed_dead_node_timer

        dead_node_list = []
        resurrected_node_list = []

        now = time.mktime(time.localtime())
        lock_resources.acquire()
        try:
            for n in node_list:
                if this_node.ip_address == n.ip_address:
                    continue
                found_new_dead_node = False
                found_resurrected_node = False
                path = os.path.join(conf.collectd_home, conf.collectd_rrd_dir, n.hostname)
                known_as_dead = n.ip_address in dead_node_set
                #FIXME: Nested try
                try:
                    min_time_diff = BIG_TIME_DIFF
                    os.path.walk(path, find_minimal_rrd_timestamp, now)
                    diff = min_time_diff

                    if diff >= dead_node_timeout and not known_as_dead:
                        logger.debug("Found dead node %s" % n.hostname)
                        logger.debug(
                            "n.hostname = %s,dead_node_set=%s," \
                            " known_as_dead %s, diff = %s "
                            % (n.hostname, dead_node_set, str(known_as_dead),
                               diff))
                        found_new_dead_node = True

                    elif diff < dead_node_timeout and known_as_dead:
                        logger.debug("Found node that resurrected from dead: %s"
                                     % n.hostname)
                        logger.debug(
                            "n.hostname = %s,dead_node_set=%s,known_as_dead %s," \
                            " diff = %s "
                            % (n.hostname, dead_node_set, str(known_as_dead),
                               diff))
                        found_resurrected_node = True

                except os.error:
                    # TODO: don't use exceptions for program flow
                        found_new_dead_node = True

                except:
                    shutdown(sys.exc_info())

                finally:
                    if found_new_dead_node:
                        logger.debug("new_dead_node_set:: %s" % new_dead_node_set)
                        if n.ip_address not in new_dead_node_set:
                            logger.info("Starting timer for new dead node")
                            new_dead_node_set.add(n.ip_address)
                            delayed_dead_node_timer = threading.Timer(
                                NODE_CREATION_TIMEOUT,
                                functools.partial(check_node_still_dead, n))
                            delayed_dead_node_timer.start()
                    if found_resurrected_node:
                        logger.info("Found resurrected node, updating collections")
                        if process_node_resurrection(
                                n, active_node_list, dead_node_set):
                            resurrected_node_list.append(n)

            if dead_node_list or resurrected_node_list:
                send(node_list, util.json_from_list(
                    active_node_list, 'active_node_list'))
                util.store_list_to_file(
                    active_node_list, active_node_list_file, this_node.group_name)

                if resurrected_node_list:
                    #mail_sender.send_node_status_alerts(
                    #     resurrected_node_list, "RESURRECTED_NODE")
                    ntf_manager.process_node_status_alerts(
                        resurrected_node_list, "RESURRECTED_NODE")

                if dead_node_list:
                    #mail_sender.send_node_status_alerts(
                    #     dead_node_list, "DEAD_NODE")
                    ntf_manager.process_node_status_alerts(
                        dead_node_list, "DEAD_NODE")

        except:
            shutdown(sys.exc_info())

        finally:
            lock_resources.release()

        return dead_node_list


    


    def update_node_collections(self, a_node_list):
        """Read a_node_list, and update active_node_list and dead_node_list,
        if needed"""

        try:
            a_node_list[:] = nodelist_reader.get_node_list(this_node, mode)

            # Check if cluster scaled out, or just created
            nodes = [n for n in a_node_list if n not in active_node_list and
                     n.ip_address not in dead_node_set]
            for m in nodes:
                active_node_list.append(m)
            if nodes:
                active_nodes_changed = True
            else:
                active_nodes_changed = False

            # Check if cluster scaled in
            nodes = [n for n in active_node_list if n not in a_node_list]
            for m in nodes:
                active_node_list.remove(m)
            if nodes:
                active_nodes_changed = True

            nodes = [ip for ip in dead_node_set
                     if not util.find_node_by_ip(ip, a_node_list)]
            for m in nodes:
                dead_node_set.remove(m)
        except ValueError:
            util.log_exception(sys.exc_info())

        return active_nodes_changed, a_node_list


    def set_master(self):
        if not node_list:
            shutdown(None, 1, "Unable to set a master for the node")
        assign_master(node_list[0])
'''

