#!/usr/bin/env python2

#
# This is NodeChecker component of Open Infinity Health Monitoring.
#

from __future__ import division          # Python 3 forward compatibility
from __future__ import print_function    # Python 3 forward compatibility

from optparse import OptionParser
import sys
import os
import subprocess
import logging.handlers
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
import listener
import control.nodemanager as nodemanager

# Constants

OI_HEALTH_MONITORING_ROOT = "OI_HEALTH_MONITORING_ROOT"
OI_COLLECTD_ROOT = "OI_COLLECTD_ROOT"
CONFIG_FILE = os.path.join("etc", "nodechecker.conf")
NODE_LIST_FILE = os.path.join("etc", "nodelist.conf")
ACTIVE_NODE_LIST_FILE = os.path.join(
      os.environ[OI_HEALTH_MONITORING_ROOT], "etc", "active_nodelist.conf")
BIG_TIME_DIFF = 1000000
RRD_HTTP_SERVER_PORT = 8181
NODE_CREATION_TIMEOUT = 500
MAX_BYTES_LOGFILE = 5000000
MAX_CMT_CONF_WAIT = 600
CMT_CONF_WAIT = 10

# Global variables

# Collections
node_list = []
active_node_list = []
dead_node_set = set()
new_dead_node_set = set()
master_list = []

# Classes
heartbeat_timer = None
heartbeat_listener = None
ntf_reader = None
nodelist_reader = None
#mail_sender = None
ntf_manager = None
conf = None
my_node = None
dead_node_timer = None
delayed_dead_node_timer = None
logger = None
lock_resources = None

# State variables
role = "SLAVE"
mode = "RUN"
my_master = None

# Configuration variables
heartbeat_period = 1
rrd_scan_period = 1
dead_node_timeout = 1
heartbeats_received = 0
min_time_diff = BIG_TIME_DIFF
loglevel = ""
logfile = ""

# HM Node Checker feature functions
def send(to_nodes, data):
    try:
        if len(to_nodes) > 0:
            logger.debug("Sending data %s" % str(data))
            for n in to_nodes:
                if n != my_node:
                    logger.debug("Sending to node %s" % str(n.ip_address))
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(data, (n.ip_address, n.port))
        else:
            shutdown(None, 1, "No nodes to send data")
    except:
        util.log_exception(sys.exc_info())


def start_heartbeat_timer():
    global heartbeat_timer
    lock_resources.acquire()
    try:
        send(node_list, my_node.to_json())
        heartbeat_timer = threading.Timer(
                          heartbeat_period, start_heartbeat_timer)
        heartbeat_timer.start()
    except:
        util.log_exception(sys.exc_info())
    finally:
        lock_resources.release()


def start_dead_node_scan_timer():
    global dead_node_timer
    dead_node_scan()
    dead_node_timer = threading.Timer(
                      rrd_scan_period, start_dead_node_scan_timer)
    dead_node_timer.start()


def cancel_timers():
    global heartbeat_timer
    global dead_node_timer
    global delayed_dead_node_timer

    if heartbeat_timer:
        heartbeat_timer.cancel()
    if dead_node_timer:
        dead_node_timer.cancel()
    if delayed_dead_node_timer:
        delayed_dead_node_timer.cancel()


def find_minimal_rrd_timestamp(arg, dirname, names):
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


def check_node_still_dead(node_to_check):
    global active_node_list
    global new_dead_node_set
    global dead_node_set
    global min_time_diff

    now = time.mktime(time.localtime())
    path = os.path.join(
           os.environ[OI_COLLECTD_ROOT], conf.collectd_rrd_dir,
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
            #mail_sender.send_node_status_alerts([node_to_check], "DEAD_NODE")
            ntf_manager.process_node_status_alerts([node_to_check], "DEAD_NODE")
            util.store_list_to_file(
                  active_node_list, ACTIVE_NODE_LIST_FILE, my_node.group_name)
        new_dead_node_set.remove(node_to_check.ip_address)
    except:
        util.log_exception(sys.exc_info())
    finally:
        lock_resources.release()


def process_node_resurrection(resurrected_node, active_nodes, dead_nodes):
    if resurrected_node in node_list:
        active_nodes.append(resurrected_node)
        dead_nodes.remove(resurrected_node.ip_address)
        return True
    else:
        return False


def dead_node_scan():
    global min_time_diff
    global new_dead_node_set
    global delayed_dead_node_timer

    dead_node_list = []
    resurrected_node_list = []

    now = time.mktime(time.localtime())
    lock_resources.acquire()
    try:
        for n in node_list:
            if my_node.ip_address == n.ip_address:
                continue
            found_new_dead_node = False
            found_resurrected_node = False
            path = os.path.join(
                   os.environ[OI_COLLECTD_ROOT], conf.collectd_rrd_dir,
                   n.hostname)
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
                          "n.hostname = %s,dead_node_set=%s,known_as_dead %s,"\
                          " diff = %s "
                          % (n.hostname, dead_node_set, str(known_as_dead),
                             diff))
                    found_resurrected_node = True

            except os.error:
                # TODO: don't use exceptions for program flow
                # There is no rrd data for the node, thus we found a dead node.
                if not known_as_dead:
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
                  active_node_list, ACTIVE_NODE_LIST_FILE, my_node.group_name)

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


def wait_for_master_heartbeats(number_of_heartbeat_periods):
    """Listens to master heartbeat signals.
    Depending on of number of received signals, a decision is made on
    how to proceed:
        - In case of too small number of signals, the node attempts to be
        itself a master.
        - In case of too big number of signals, if the node is a slave, it
        checks if it should itself run as a slave.
    """
    global heartbeats_received
    global master_list

    ret = "FINE"
    heartbeats_received = 0
    master_list[:] = []

    # Sleep, count masters when awake, then all your base are belong to us.
    time.sleep(number_of_heartbeat_periods * heartbeat_period)
    lock_resources.acquire()
    try:
        if my_node.role == "MASTER":
            expected_masters = 0
        else:
            expected_masters = 1

        if (len(master_list) < expected_masters):
            ret = "TOO_LOW"
        elif (len(master_list) > expected_masters):
            ret = "TOO_HIGH"
        if my_node.role == "SLAVE" and master_list:
            if my_master not in master_list:
                assign_master(master_list[0])
    except:
        util.log_exception(sys.exc_info())
    finally:
        lock_resources.release()
    return ret


def assign_master(new_master):
    global my_master
    logger.info("Configuring node name %s as a SLAVE, master name is %s"
                 % (my_node.hostname, new_master.hostname))
    my_master = new_master
    nodemanager.configure_node_as_slave(my_node.ip_address,
                                        RRD_HTTP_SERVER_PORT,
                                        my_master.ip_address,
                                        RRD_HTTP_SERVER_PORT)

# HM Node Checker algorithm functions


def become_a_master():
    """Triggers actions needed to prepare the node for running
    in MASTER role. Runs the master loop.
    """
    global delayed_dead_node_timer

    if my_node.role != "MASTER":
        my_node.role = "MASTER"
        logger.info("This node became a MASTER")
        delayed_dead_node_timer = threading.Timer(dead_node_timeout,
                                                  start_dead_node_scan_timer)
        delayed_dead_node_timer.start()
        start_heartbeat_timer()
        nodemanager.configure_node_as_master(my_node.ip_address)
        util.store_list_to_file(active_node_list, ACTIVE_NODE_LIST_FILE,
                                my_node.group_name)
    master_loop()


def become_a_slave():
    global my_node
    global node_list
    logger.info("Trying to become a SLAVE")
    if my_node.role == "MASTER":
        cancel_timers()
        my_node.role = "SLAVE"
        if master_list:
            assign_master(master_list[0])
        else:
            shutdown(None, 1, "Unable to set a master for the node")
    slave_loop(node_list)


def continue_as_master():
    """Returns True if a node should continue in master role"""
    try:
        ret = True
        my_pos = active_node_list.index(my_node)
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


def member_initiation_procedure():
    a = 0
    while True:
        try:
            my_pos = active_node_list.index(my_node)
            logger.debug("My position in the list is %d, a = %d" % (my_pos, a))
            if wait_for_master_heartbeats(1) == "TOO_LOW":
                if a == my_pos:
                    become_a_master()
                a = (a + 1) % len(active_node_list)
            else:
                become_a_slave()
        except:
            shutdown(sys.exc_info())


def master_loop():
    global node_list
    global active_node_list
    global dead_node_set
    logger.info("Master Loop start")
    while True:
        # 1) Check number of masters
        if wait_for_master_heartbeats(1) == "TOO_HIGH":
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
            util.store_list_to_file(active_node_list, ACTIVE_NODE_LIST_FILE,
                                    my_node.group_name)
        # 5) release lock
        lock_resources.release()

    # Can not continue as master
    become_a_slave()


def slave_loop(a_node_list):
    logger.info("Slave Loop start")
    while True:
        try:
            update_node_collections(a_node_list)
            if wait_for_master_heartbeats(2) == "TOO_LOW":
                break
        except:
            shutdown(sys.exc_info())


def configure_logger():
    global logger
    global loglevel
    global logfile
    logger = logging.getLogger('nodechecker')
    handler = logging.handlers.RotatingFileHandler(
              logfile, maxBytes=MAX_BYTES_LOGFILE, backupCount=5)
    if loglevel == "debug":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] "\
                                  " [%(funcName)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def process_command_line(argv):
    if argv is None:
        argv = sys.argv[1:]
    parser = OptionParser()
    parser.add_option("--loglevel", dest="loglevel",
                      help="log level",  metavar="LOGLEVEL")
    parser.add_option("--logfile", dest="logfile",
                      help="location of the log file", metavar="LOGFILE")
    parser.add_option("--hostname", dest="hostname",
                      help="hostname of this node", metavar="HOSTNAME")
    parser.add_option("--port", dest="port",
                      help="use the given port instead of default one",
                      metavar="PORT")
    parser.add_option("--ip-address", dest="ip_address",
                      help="IP address of this node", metavar="IPADDRESS")
    parser.add_option("--ip-address-public", dest="ip_address_public",
                      help="public IP address of this node",
                      metavar="IPADDRESSPUBLIC")
    parser.add_option("--instance-id", dest="instance_id",
                      help="cmt instance id of this node",
                      metavar="INSTANCEshutdownID")
    parser.add_option("--cluster-id", dest="cluster_id",
                      help="cmt cluster id this node", metavar="CLUSTERID")
    parser.add_option("--machine-id", dest="machine_id",
                      help="cmt machine id of this node", metavar="MACHINEID")
    parser.add_option("--cloud-zone", dest="cloud_zone",
                      help="cmt cloud zone of this node", metavar="CLOUDZONE")
    parser.add_option("--mode", dest="mode",
                      help="TEST to run instances on single machine,"\
                      "otherwise RUN. ", metavar="MODE")
    (options, args) = parser.parse_args()
    return options, args


def process_settings(options, conf, node):
    global loglevel, logfile, mode
    global heartbeat_period, rrd_scan_period, dead_node_timeout

    heartbeat_period = int(conf.node_heartbeat_period)
    rrd_scan_period = int(conf.node_rrd_scan_period)
    dead_node_timeout = int(conf.node_dead_node_timeout)

    if options.loglevel:
        loglevel = options.loglevel
    else:
        loglevel = conf.node_log_level

    if options.logfile:
        logfile = options.logfile
    else:
        logfile = conf.node_log_file

    if options.port:
        node.port = int(options.port)
    else:
        node.port = int(conf.node_udp_port)

    if options.ip_address:
        node.ip_address = options.ip_address
    elif conf.node_ip_address == "auto":
        node.ip_address = util.get_ip_address()
    else:
        node.ip_address = conf.node_ip_address

    if options.ip_address_public:
        node.ip_address_public = options.ip_address_public
    elif conf.node_ip_address_public == "auto":
        node.ip_address_public = os.environ["OI_PUBLIC_IP"]
    else:
        node.ip_address_public = conf.node_ip_address_public

    if options.instance_id:
        node.instance_id = options.instance_id
    elif conf.node_instance_id == "auto":
        node.instance_id = os.environ["OI_INSTANCE_ID"]
    else:
        node.instance_id = conf.instance_id

    if options.cluster_id:
        node.cluster_id = options.cluster_id
    elif conf.node_cluster_id == "auto":
        node.cluster_id = os.environ["OI_CLUSTER_ID"]
    else:
        node.cluster_id = conf.node_cluster_id

    if options.machine_id:
        node.machine_id = options.machine_id
    elif conf.node_machine_id == "auto":
        node.machine_id = os.environ["OI_MACHINE_ID"]
    else:
        node.machine_id = conf.node_machine_id

    if options.cloud_zone:
        node.cloud_zone = options.cloud_zone
    elif conf.node_cloud_zone == "auto":
        node.cloud_zone = os.environ["OI_CLOUD_ZONE"]
    else:
        node.cloud_zone = conf.node_cloud_zone

    if options.mode:
        mode = options.mode
    else:
        mode = conf.node_mode


def wait_for_machine_configured(file_reader):
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
            if util.get_hostname() != my_node.hostname:
                logger.debug("Sleep")
                total_sleep_time += CMT_CONF_WAIT
                if  total_sleep_time >= MAX_CMT_CONF_WAIT:
                    shutdown(None, 1, "This is boring, bye.")
                time.sleep(CMT_CONF_WAIT)
            else:
                # sleep once more before the exit: to make sure that hostname
                # change propagated
                time.sleep(CMT_CONF_WAIT)
                break


def update_node_collections(a_node_list):
    """Read a_node_list, and update active_node_list and dead_node_list,
    if needed"""

    try:
        a_node_list[:] = nodelist_reader.get_node_list(my_node, mode)

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


def set_master():
    if not node_list:
        shutdown(None, 1, "Unable to set a master for the node")
    assign_master(node_list[0])


def init(settings):
    global my_node, ntf_reader, nodelist_reader, ntf_manager, conf
    global heartbeat_listener, active_node_list, dead_node_set, node_list
    global heartbeats_received, master_list, lock_resources

    # Construct configuration file reader
    config_file = os.path.join(os.environ[OI_HEALTH_MONITORING_ROOT],
                               CONFIG_FILE)
    conf = config.Config(config_file)

    # Construct node
    my_node = node.Node()
    process_settings(settings, conf, my_node)
    configure_logger()
    nodelist_reader = reader.Reader(os.path.join(
          os.environ[OI_HEALTH_MONITORING_ROOT], NODE_LIST_FILE))
    my_node.group_name = nodelist_reader.get_attribute(my_node.ip_address,
                                                       'GROUP_NAME')
    my_node.machine_type = nodelist_reader.get_attribute(my_node.ip_address,
                                                         'MACHINE_TYPE')
    my_node.hostname = nodelist_reader.get_attribute(my_node.ip_address,
                                                     'HOST_NAME')

    # Construct remaining members
    lock_resources = threading.RLock()
    ntf_reader = notification.parser.NotificationParser(my_node, conf)
    #mail_sender = notification.mailsender.MailSender(conf, my_node)
    ntf_manager = notification.manager.NotificationManager(my_node, conf)
    heartbeat_listener = listener.HeartbeatListener(my_node,
                                                    heartbeats_received,
                                                    master_list,
                                                    active_node_list,
                                                    lock_resources)

    # Prepare node collections
    node_list = update_node_collections(node_list)[1]
    wait_for_machine_configured(nodelist_reader)
    set_master()


def run():
    try:
        logger.info("Starting")
        heartbeat_listener.start()
        member_initiation_procedure()

    except KeyboardInterrupt:
        shutdown(None, 0, "Keyboard interrupt, shutting down")


def shutdown(exc_info=None, exit_status=1, message="Shutting down"):
    util.log_message(message, exc_info)
    heartbeat_listener.shutdown()
    cancel_timers()
    sys.exit(exit_status)


def start():
    init(None)
    run()


def main(argv=None):
    settings = process_command_line(argv)[0]
    init(settings)
    run()
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
