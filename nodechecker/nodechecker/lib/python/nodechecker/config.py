#!/usr/bin/env python2

import ConfigParser


class Config(object):

    def __init__(self, conf_file):
        config = ConfigParser.SafeConfigParser()
        config.read(conf_file)

        self.node_mode = config.get('node', 'mode')
        self.node_log_level = config.get('node', 'log_level')
        self.node_log_file = config.get('node', 'log_file')
        self.node_udp_port = config.get('node', 'udp_port')
        self.node_ip_address = config.get('node', 'ip_address')
        self.node_ip_address_public = config.get('node', 'ip_address_public')
        self.node_instance_id = config.get('node', 'instance_id')
        self.node_cluster_id = config.get('node', 'cluster_id')
        self.node_machine_id = config.get('node', 'machine_id')
        self.node_cloud_zone = config.get('node', 'cloud_zone')
        self.node_heartbeat_period = config.get('node', 'heartbeat_period')
        self.node_rrd_scan_period = config.get('node', 'rrd_scan_period')
        self.node_dead_node_timeout = config.get('node', 'dead_node_timeout')

        self.notifications_log_file = config.get('notifications', 'log_file')
        self.notifications_log_file_max_bytes = config.get('notifications', 'log_file_max_bytes')
        self.notifications_home_dir = config.get('notifications', 'home_dir')
        self.notification_inbox_dir = config.get('notifications', 'inbox_dir')
        self.notifications_sent_dir = config.get('notifications', 'sent_dir')
        self.notifications_dead_node_string = config.get('notifications', 'dead_node_string')

        self.email_use = config.get('email', 'use')
        self.email_subject = config.get('email', 'subject')
        self.email_from = config.get('email', 'from')
        self.email_to = config.get('email', 'to')
        self.email_smpt_server = config.get('email', 'smpt_server')

        self.collectd_rrd_dir = config.get('collectd', 'rrd_dir')

        self.test_dump_dir = config.get('test', 'dump_dir')
