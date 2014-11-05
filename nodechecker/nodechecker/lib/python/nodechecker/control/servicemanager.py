#!/usr/bin/env python2

# FIXME
#from nodechecker.nodechecker import *
import nodechecker.nodechecker
import daemon
import os
import subprocess
import nodechecker.control.nodemanager

NODECHECKER_PID_FILE = 'var/run/oi3-nodechecker.pid'
START_SCRIPT = "bin/start.sh"
STOP_SCRIPT = "bin/stop.sh"
COLLECTD_STOP_SCRIPT = 'sbin/restart.sh'
SUDO = 'sudo'


class NodecheckerDaemon(daemon.Daemon):
    def run(self):
        #node_manager = control.nodemanager.NodeManager(conf)
        nodechecker.nodechecker.start(self.conf, self.node_manager)


class ServiceManager(object):
    def __init__(self, conf, pid_file=None, user='nodechecker'):
        self.conf = conf
        self.node_manager = nodechecker.control.nodemanager.NodeManager(conf)
        self.pid_file = pid_file if pid_file else os.path.join(conf.hm_root, NODECHECKER_PID_FILE)
        self.user = user
        self.nodechecker_daemon = None

    def start_services(self):
        """Starts nodechecker.
        Nodechecker then runs in slave or master mode, and calls
        configure_node_as_master(), or configure_node_as_master()
        to complete health monitoring start up
        """
        self.nodechecker_daemon = NodecheckerDaemon(self.pid_file,
                                                    conf=self.conf,
                                                    node_manager=self.node_manager,
                                                    username=self.user)
        self.nodechecker_daemon.start()

    def stop_services(self):
        self.nodechecker_daemon.stop()
        subprocess.Popen([SUDO, os.path.join(self.conf.collectd_home, COLLECTD_STOP_SCRIPT)])
        subprocess.Popen([SUDO, os.path.join(self.conf.pound_home, STOP_SCRIPT)])
        subprocess.Popen([SUDO, os.path.join(self.conf.rrd_http_server_home, STOP_SCRIPT)])



