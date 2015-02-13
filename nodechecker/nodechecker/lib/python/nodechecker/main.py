#!/usr/bin/env python2

#
# Main thread of nodechecker
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility

from optparse import OptionParser
import sys
import signal
import time
import config

import util
import context
import manager

mgr = None
logger = None


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


def init(settings=None, conf_obj=None, config_file=None, node_manager_obj=None):
    global mgr, logger

    conf = conf_obj if conf_obj else config.Config(config_file)
    ctx = context.Context(settings, conf, node_manager_obj)
    logger = ctx.logger

    # Setup signal handlers
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigint_handler)

    # Setup event
    #stop_event = threading.Event()

    # master-slave management, running the main loop of the program
    mgr = manager.Manager(ctx)
    #mgr.start()


def sigterm_handler(signum, frame):
    logger.debug("SIGTERM received")
    stop(None, 0, "Keyboard interrupt, shutting down")


def sigint_handler(signum, frame):
    logger.debug("SIGINT received")
    stop(None, 0, "Keyboard interrupt, shutting down")


def run():
    try:
        logger.info("Starting...")
        mgr.start()

    except KeyboardInterrupt:
       stop(None, 0, "Keyboard interrupt, shutting down")


def stop(exc_info=None, exit_status=1, message="Shutting down"):
    #util.log_message(message, exc_info)
    time.sleep(5)
    mgr.shutdown()
    #sys.exit(exit_status)


def start(conf_obj, node_manager_obj):
    init(conf_obj=conf_obj, node_manager_obj=node_manager_obj)
    run()


def main(argv=None):
    #settings = process_command_line(argv)[0]
    init(settings=process_command_line(argv)[0], config_file="")
    run()
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
