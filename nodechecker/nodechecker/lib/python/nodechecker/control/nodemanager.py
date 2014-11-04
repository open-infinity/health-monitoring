#!/usr/bin/env python2

import os
import sys
import logging
import shutil
import fileinput
import nodechecker.util
import subprocess
import nodechecker.config

START_SCRIPT = "bin/start.sh"
STOP_SCRIPT = "bin/stop.sh"
RESTART_SCRIPT = "/bin/restart.sh"
SUDO = 'sudo'
COLLECTD_MODE_CLIENT = 'client'
COLLECTD_MODE_SERVER = 'server'
COLLECTD_NETWORK_CONF_FILE = 'etc/collectd.d/network.conf'
COLLECTD_RESTART_SCRIPT = 'sbin/restart.sh'
POUND_CONFIG_TEMPLATE_FILE = 'var/share/pound/pound.cfg.tpl'


class NodeManager(object):
    def __init__(self, conf):
        self.conf = conf
        self.logger = logging.getLogger('nodechecker.nodemanager')

    def configure_node_as_master(self, own_ip):
        self.configure_and_restart_collectd(own_ip, COLLECTD_MODE_SERVER)
        subprocess.Popen([SUDO, os.path.join(self.conf.hm_root, self.conf.pound_home, STOP_SCRIPT)])
        subprocess.Popen([SUDO, os.path.join(self.conf.hm_root, self.conf.rrd_http_server_home, START_SCRIPT)])

    def configure_node_as_slave(self, own_ip, own_port, server_ip, server_port):
        subprocess.Popen([SUDO, os.path.join(self.conf.hm_root, self.conf.rrd_http_server_home, STOP_SCRIPT)])
        self.configure_and_restart_collectd(server_ip, COLLECTD_MODE_CLIENT)
        self.configure_and_restart_pound(own_ip, own_port, server_ip, server_port)

    def configure_and_restart_collectd(self, ip, mode):
        if mode not in [COLLECTD_MODE_CLIENT, COLLECTD_MODE_SERVER]:
            self.logger.error("Error configuring collectd")
            return
        tpl_file = "var/share/collectd/%s.tpl" % (mode)
        src = os.path.join(self.conf.hm_root, self.conf.nodechecker_home, tpl_file)
        dst = os.path.join(self.conf.hm_root, self.conf.collectd_home, COLLECTD_NETWORK_CONF_FILE)
        temp = src + ".temp"
        try:
            shutil.copyfile(src, temp)
            for line in fileinput.input(temp, inplace=1):
                if mode == "client":
                    print line.replace("SERVER_IP", ip),
                else:
                    if line.find("LISTEN_IP") >= 0:
                        print line.replace("LISTEN_IP", ip),
                    elif line.find("RRD_DATA_DIR") >= 0:
                        print line.replace("RRD_DATA_DIR",
                                           os.path.join(self.conf.hm_root, self.conf.collectd_rrd_dir)),
                    else:
                        print line,
            shutil.copyfile(temp, dst)
        except:
            nodechecker.util.log_exception(sys.exc_info())
        subprocess.Popen([SUDO, os.path.join(self.conf.hm_root,
                                             self.conf.collectd_home,
                                             COLLECTD_RESTART_SCRIPT)])

    def configure_and_restart_pound(self, own_ip, own_port, server_ip, server_port):
        global logger
        try:
            tpl_file = os.path.join(self.conf.hm_root, self.conf.nodechecker_home, POUND_CONFIG_TEMPLATE_FILE)
            temp_file = tpl_file + ".temp"
            conf_file = "etc/pound.cfg"
            shutil.copyfile(tpl_file, temp_file)
            for line in fileinput.input(temp_file, inplace=1):
                if line.find("OWN_IP") >= 0:
                    print line.replace("OWN_IP", own_ip),
                elif line.find("OWN_PORT") >= 0:
                    print line.replace("OWN_PORT", repr(own_port)),
                elif line.find("SERVER_IP") >= 0:
                    print line.replace("SERVER_IP", server_ip),
                elif line.find("SERVER_PORT") >= 0:
                    print line.replace("SERVER_PORT", repr(server_port)),
                else:
                    print line,
            shutil.copyfile(temp_file, conf_file)
        except:
            nodechecker.util.log_exception(sys.exc_info())
        subprocess.Popen(['sudo', os.path.join(self.conf.hm_root, self.conf.pound_home, RESTART_SCRIPT)])

