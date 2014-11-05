#!/usr/bin/env python2

#
# This is NodeChecker component of Open Infinity Health Monitoring.
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility

from optparse import OptionParser
import sys
import os
import signal
import logging.handlers
import threading
import time
import config
import notification.parser
import notification.manager
import reader
import util
import node
import udp_listener

# Constants
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
node_manager = None
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
log_level = ""
log_file = ""
node_list_file = ""
active_node_list_file = ""


def configure_logger():
    global logger
    global log_level
    global log_file
    global conf
    logger = logging.getLogger('nodechecker')
    log_file_path = os.path.join(conf.hm_root, conf.nodechecker_home, log_file)
    handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=MAX_BYTES_LOGFILE, backupCount=5)
    if log_level == "debug":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] "
                                  " [%(funcName)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def process_command_line(argv):
    if argv is None:
        argv = sys.argv[1:]
    parser = OptionParser()
    parser.add_option("--log_level", dest="log_level",
                      help="log level", metavar="log_level")
    parser.add_option("--log_file", dest="log_file",
                      help="location of the log file", metavar="log_file")
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
                      help="TEST to run instances on single machine," \
                           "otherwise RUN. ", metavar="MODE")
    (options, args) = parser.parse_args()
    return options, args


def process_settings(options, conf, node):
    global log_level, log_file, mode
    global heartbeat_period, rrd_scan_period, dead_node_timeout

    heartbeat_period = int(conf.node_heartbeat_period)
    rrd_scan_period = int(conf.node_rrd_scan_period)
    dead_node_timeout = int(conf.node_dead_node_timeout)

    if options and options.log_level:
        log_level = options.log_level
    else:
        log_level = conf.node_log_level

    if options and options.log_file:
        log_file = options.log_file
    else:
        log_file = conf.node_log_file

    if options and options.port:
        node.port = int(options.port)
    else:
        node.port = int(conf.node_udp_port)

    if options and options.ip_address:
        node.ip_address = options.ip_address
    elif conf.node_ip_address == "auto":
        node.ip_address = util.get_ip_address()
    else:
        node.ip_address = conf.node_ip_address

    if options and options.ip_address_public:
        node.ip_address_public = options.ip_address_public
        
    # can't know which ip address to use automatically. this must be configured in config file    
    #elif conf.node_ip_address_public == "auto":
    #    node.ip_address_public = os.environ["OI_PUBLIC_IP"]
    else:
        node.ip_address_public = conf.node_ip_address_public

    if options and options.instance_id:
        node.instance_id = options.instance_id
    #elif conf.node_instance_id == "auto":
    #    node.instance_id = os.environ["OI_INSTANCE_ID"]
    else:
        node.instance_id = conf.node_instance_id

    if options and options.cluster_id:
        node.cluster_id = options.cluster_id
    #elif conf.node_cluster_id == "auto":
    #    node.cluster_id = os.environ["OI_CLUSTER_ID"]
    else:
        node.cluster_id = conf.node_cluster_id

    if options and options.machine_id:
        node.machine_id = options.machine_id
    #elif conf.node_machine_id == "auto":
    #    node.machine_id = os.environ["OI_MACHINE_ID"]
    else:
        node.machine_id = conf.node_machine_id

    if options and options.cloud_zone:
        node.cloud_zone = options.cloud_zone
    #elif conf.node_cloud_zone == "auto":
    #    node.cloud_zone = os.environ["OI_CLOUD_ZONE"]
    else:
        node.cloud_zone = conf.node_cloud_zone

    if options and options.mode:
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
                if total_sleep_time >= MAX_CMT_CONF_WAIT:
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


def init(settings=None, conf_obj=None, config_file=None, node_manager_obj=None):
    global my_node, ntf_reader, nodelist_reader, ntf_manager, conf
    global heartbeat_listener, active_node_list, dead_node_set, node_list
    global heartbeats_received, master_list, lock_resources
    global node_list_file, active_node_list_file
    global node_manager

    conf = conf_obj if conf_obj else config.Config(config_file)
    node_manager = node_manager_obj

    node_list_file = os.path.join(conf.hm_root, 'nodechecker', "etc", "nodelist.conf")
    active_node_list_file = os.path.join(conf.hm_root, 'nodechecker', "etc", "active_nodelist.conf")

    # Construct node
    my_node = node.Node()
    process_settings(settings, conf, my_node)
    configure_logger()
    nodelist_reader = reader.Reader(node_list_file)
    my_node.group_name = nodelist_reader.get_attribute(my_node.ip_address,
                                                       'GROUP_NAME')
    my_node.machine_type = nodelist_reader.get_attribute(my_node.ip_address,
                                                         'MACHINE_TYPE')
    my_node.hostname = nodelist_reader.get_attribute(my_node.ip_address,
                                                     'HOST_NAME')

    # Construct remaining members
    lock_resources = threading.RLock()
    ntf_reader = notification.parser.NotificationParser(my_node, conf)
    ntf_manager = notification.manager.NotificationManager(my_node, conf)
    heartbeat_listener = udp_listener.UDPSocketListener(my_node,
                                                    heartbeats_received,
                                                    master_list,
                                                    active_node_list,
                                                    lock_resources)

    # Prepare node collections
    node_list = update_node_collections(node_list)[1]
    wait_for_machine_configured(nodelist_reader)
    set_master()


def sigterm_handler(signum, frame):
    logger.debug("SIGTERM received")
    shutdown(None, 0, "Keyboard interrupt, shutting down")


def sigint_handler(signum, frame):
    logger.debug("SIGINT received")
    shutdown(None, 0, "Keyboard interrupt, shutting down")


def run():
    try:
        logger.info("Starting...")
        heartbeat_listener.start()
        member_initiation_procedure()

    except KeyboardInterrupt:
        shutdown(None, 0, "Keyboard interrupt, shutting down")


def shutdown(exc_info=None, exit_status=1, message="Shutting down"):
    util.log_message(message, exc_info)
    heartbeat_listener.shutdown()
    cancel_timers()
    sys.exit(exit_status)


def start(conf_obj, node_manager_obj):
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigint_handler)

    init(conf_obj=conf_obj, node_manager_obj=node_manager_obj)

    run()


#def init(settings=None, conf_obj=None, config_file=None):


def main(argv=None):
    #settings = process_command_line(argv)[0]
    init(settings=process_command_line(argv)[0], config_file="")
    run()
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
