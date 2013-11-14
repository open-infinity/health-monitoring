#!/usr/bin/env python2

import os
import sys
import logging
import shutil
import fileinput
import sysutil
import nodechecker.util

TOAS_HEALTH_MONITORING_ROOT = os.environ["TOAS_HEALTH_MONITORING_ROOT"]
TOAS_COLLECTD_ROOT = os.environ["TOAS_COLLECTD_ROOT"]
RRD_DIR = os.path.join(TOAS_COLLECTD_ROOT, "var/lib/collectd/rrd")
POUND_TPL_FILE = "var/share/pound/pound.cfg.tpl"
POUND_CFG_FILE = "/etc/pound.cfg"

logger = logging.getLogger('nodechecker.nodemanager')


def configure_node_as_master(own_ip):
    configure_and_restart_collectd(own_ip, "server")
    sysutil.systemV_service_command('rrd-http-server', 'start')
    sysutil.systemV_service_command('pound', 'stop')


def configure_node_as_slave(own_ip, own_port, server_ip, server_port):
    sysutil.systemV_service_command('rrd-http-server', 'stop')
    configure_and_restart_collectd(server_ip, "client")
    configure_and_restart_pound(own_ip, own_port, server_ip, server_port)


def configure_and_restart_collectd(ip, mode):
    global logger
    if mode not in ["client", "server"]:
        logger.error("Error configuring collectd")
        return
    tpl_file = "var/share/collectd/%s.tpl" % (mode)
    src = os.path.join(TOAS_HEALTH_MONITORING_ROOT, tpl_file)
    dst = os.path.join(TOAS_COLLECTD_ROOT, "etc/collectd.d/network.conf")
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
    sysutil.systemV_service_command('collectd', 'restart')


def configure_and_restart_pound(own_ip, own_port, server_ip, server_port):
    global logger
    src = os.path.join(TOAS_HEALTH_MONITORING_ROOT, POUND_TPL_FILE)
    dst = POUND_CFG_FILE
    try:
        shutil.copyfile(src, dst)
        for line in fileinput.input(dst, inplace=1):
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
    sysutil.systemV_service_command('pound', 'restart')
