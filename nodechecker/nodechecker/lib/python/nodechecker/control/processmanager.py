#!/usr/bin/env python2

# FIXME
from nodechecker.nodechecker import *
import daemon
import sysutil

NODECHECKER_PID_FILE = '/var/run/oi3-healthmonitoring.pid'


class NodecheckerDaemon(daemon.Daemon):
    def run(self):
        # FIXME
        main()


def start_health_monitoring():
    """Starts nodechecker.
    Nodechecker then runs in slave or master mode, and calls
    configure_node_as_master(), or configure_node_as_master()
    to compolete health monitoring start up
    """
    start_nodechecker()


def stop_health_monitoring():
    stop_nodechecker()
    sysutil.systemV_service_command('oi3-rrd-http-server', 'stop')
    sysutil.systemV_service_command('oi3-collectd', 'stop')
    sysutil.systemV_service_command('pound', 'stop')


def start_nodechecker():
    nodechecker_daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    nodechecker_daemon.start()


def stop_nodechecker():
    nodechecker_daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    nodechecker_daemon.stop()
