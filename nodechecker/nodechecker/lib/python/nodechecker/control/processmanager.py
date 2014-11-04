#!/usr/bin/env python2

# FIXME
from nodechecker.nodechecker import *
import daemon
import os
import subprocess

OI_ROOT=os.environ["OI_ROOT"]
NODECHECKER_PID_FILE = os.path.join(OI_ROOT, 'healthmonitoring/nodechecker/var/run/oi3-nodechecker.pid')

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
    subprocess.Popen(['sudo', os.path.join(OI_ROOT, "healthmonitoring/collectd/sbin/stop.sh")])
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/pound/bin/stop.sh")])
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/rrd-http-server/bin/stop.sh")])


def start_nodechecker():
    nodechecker_daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    nodechecker_daemon.start()


def stop_nodechecker():
    nodechecker_daemon = NodecheckerDaemon(NODECHECKER_PID_FILE)
    nodechecker_daemon.stop()
