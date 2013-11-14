#!/usr/bin/env python2

# FIXME
from nodechecker.nodechecker import *
import daemon
import sysutil

NODECHECKER_PID_FILE = '/var/run/oi-healthmonitoring.pid'


class NodecheckerDaemon(daemon.Daemon):
    def run(self):
        # FIXME
        main()


def start_toas_health_monitoring():
    """Starts nodechecker.
    Nodechecker then runs in slave or master mode, and calls
    configure_node_as_master(), or configure_node_as_master()
    to compolete health monitoring start up
    """
    start_nodechecker()


def stop_toas_health_monitoring():
    stop_nodechecker()
    sysutil.systemV_service_command('rrd-http-server', 'stop')
    sysutil.systemV_service_command('collectd', 'stop')
    sysutil.systemV_service_command('pound', 'stop')


def start_nodechecker():
    daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    daemon.start()


def stop_nodechecker():
    daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    daemon.stop()
