#!/usr/bin/env python2

import os
import sys
import logging
import shutil
import fileinput
import nodechecker.util
import subprocess

OI_ROOT = os.environ["OI_ROOT"]
RRD_DIR = os.path.join(OI_ROOT, "healthmonitoring/collectd/var/lib/collectd/rrd")
POUND_TPL_FILE = os.path.join(OI_ROOT, "nodechecker/var/share/pound/pound.cfg.tpl")
POUND_CFG_FILE = os.path.join(OI_ROOT, "healthmonitoring/pound/etc/pound.cfg")

logger = logging.getLogger('nodechecker.nodemanager')


def configure_node_as_master(own_ip):
    configure_and_restart_collectd(own_ip, "server")
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/pound/bin/stop.sh")])
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/rrd-http-server/bin/start.sh")])


def configure_node_as_slave(own_ip, own_port, server_ip, server_port):
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/rrd-http-server/bin/stop.sh")])
    configure_and_restart_collectd(server_ip, "client")
    configure_and_restart_pound(own_ip, own_port, server_ip, server_port)


def configure_and_restart_collectd(ip, mode):
    global logger
    if mode not in ["client", "server"]:
        logger.error("Error configuring collectd")
        return
    tpl_file = "var/share/collectd/%s.tpl" % (mode)
    src = os.path.join(OI_ROOT, "healthmonitoring/nodechecker", tpl_file)
    dst = os.path.join(OI_ROOT, "healthmonitoring/collectd/etc/collectd.d/network.conf")
    try:
        shutil.copyfile(src, dst)
        for line in fileinput.input(dst, inplace=1):
            if mode == "client":
                print line.replace("SERVER_IP", ip),
            else:
                if line.find("LISTEN_IP") >= 0:
                    print line.replace("LISTEN_IP", ip),
                elif line.find("RRD_DATA_DIR") >= 0:
                    print line.replace("RRD_DATA_DIR", RRD_DIR),
                else:
                    print line,
    except:
        nodechecker.util.log_exception(sys.exc_info())
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/collectd/sbin/restart.sh")])


def configure_and_restart_pound(own_ip, own_port, server_ip, server_port):
    global logger
    try:
        shutil.copyfile(POUND_TPL_FILE, POUND_CFG_FILE)
        for line in fileinput.input(POUND_CFG_FILEt, inplace=1):
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
    except:
        nodechecker.util.log_exception(sys.exc_info())
    subprocess.Popen([ 'sudo', os.path.join(OI_ROOT, "healthmonitoring/pound/bin/restart.sh")])

