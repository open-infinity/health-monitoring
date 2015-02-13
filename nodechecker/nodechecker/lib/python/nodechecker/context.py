import os
import node
import util
import threading
import filereader
import logging
import logging.handlers
import notification.parser
import notification.manager


class Context(object):


    def __init__(self, options=None, conf=None, node_manager_obj=None):

        # ---------------- Default values ----------------
        # Parameters
        self.BIG_TIME_DIFF = 1000000
        self.RRD_HTTP_SERVER_PORT = 8181
        self.NODE_CREATION_TIMEOUT = 500
        self.MAX_BYTES_LOGFILE = 5000000
        self.MAX_CMT_CONF_WAIT = 600
        self.CMT_CONF_WAIT = 10

        # Runtime collections
        self.node_list = []
        self.active_node_list = []
        self.dead_node_set = set()
        self.new_dead_node_set = set()
        self.master_list = []

        # Runtime classes
        #self.udp_listener = None
        self.ntf_reader = None
        self.nodelist_reader = None
        self.ntf_manager = None
        self.node_manager = None
        self.conf = None
        self.this_node = None
        #self.timer_dead_node = None
        #self.timer_delayed_dead_node = None
        #self.timer_heartbeat = None
        self.logger = None
        self.resource_lock = None

        # State variables
        #role = "SLAVE"
        self.mode = "RUN"
        self.my_master = None

        # Configuration variables
        self.heartbeat_period = 1
        self.rrd_scan_period = 1
        self.dead_node_timeout = 1
        self.heartbeats_received = 0
        self.min_time_diff = self.BIG_TIME_DIFF
        self.log_level = ""
        self.log_file = ""
        self.node_list_file = ""
        self.active_node_list_file = ""
        # ---------------- End of default values ----------------

        # Extract properties from configuration file or command line
        self.this_node = node.Node()
        self.conf = conf

        if self.conf:
            self.node_list_file = os.path.join(conf.hm_root, 'nodechecker', "etc", "nodelist.conf")
            self.active_node_list_file = os.path.join(conf.hm_root, 'nodechecker', "etc", "active_nodelist.conf")
            self.nodelist_reader = filereader.FileReader(self.node_list_file)
            self.node_manager = node_manager_obj
            self.heartbeat_period = int(conf.node_heartbeat_period)
            self.rrd_scan_period = int(conf.node_rrd_scan_period)
            self.dead_node_timeout = int(conf.node_dead_node_timeout)

            if options and options.log_level:
                self.log_level = options.log_level
            else:
                self.log_level = conf.node_log_level

            if options and options.log_file:
                self.log_file = options.log_file
            else:
                self.log_file = conf.node_log_file

            if options and options.port:
                self.this_node.port = int(options.port)
            else:
                self.this_node.port = int(conf.node_udp_port)

            if options and options.ip_address:
                self.this_node.ip_address = options.ip_address
            elif conf.node_ip_address == "auto":
                self.this_node.ip_address = util.get_ip_address()
            else:
                self.this_node.ip_address = conf.node_ip_address

            if options and options.ip_address_public:
                self.this_node.ip_address_public = options.ip_address_public

            # can't know which ip address to use automatically. this must be configured in config file
            #elif conf.node_ip_address_public == "auto":
            #    node.ip_address_public = os.environ["OI_PUBLIC_IP"]
            else:
                self.this_node.ip_address_public = conf.node_ip_address_public

            if options and options.instance_id:
                self.this_node.instance_id = options.instance_id
            #elif conf.node_instance_id == "auto":
            #    node.instance_id = os.environ["OI_INSTANCE_ID"]
            else:
                self.this_node.instance_id = conf.node_instance_id

            if options and options.cluster_id:
                self.this_node.cluster_id = options.cluster_id
            #elif conf.node_cluster_id == "auto":
            #    node.cluster_id = os.environ["OI_CLUSTER_ID"]
            else:
                self.this_node.cluster_id = conf.node_cluster_id

            if options and options.machine_id:
                self.this_node.machine_id = options.machine_id
            #elif conf.node_machine_id == "auto":
            #    node.machine_id = os.environ["OI_MACHINE_ID"]
            else:
                self.this_node.machine_id = conf.node_machine_id

            if options and options.cloud_zone:
                self.this_node.cloud_zone = options.cloud_zone
            #elif conf.node_cloud_zone == "auto":
            #    node.cloud_zone = os.environ["OI_CLOUD_ZONE"]
            else:
                self.this_node.cloud_zone = conf.node_cloud_zone

            if options and options.mode:
                self.mode = options.mode
            else:
                self.mode = conf.node_mode

            # Construct the rest
            if self.nodelist_reader:
                self.this_node.group_name = self.nodelist_reader.read_attribute(self.this_node.ip_address, 'GROUP_NAME')
                self.this_node.machine_type = self.nodelist_reader.read_attribute(self.this_node.ip_address, 'MACHINE_TYPE')
                self.this_node.hostname = self.nodelist_reader.read_attribute(self.this_node.ip_address, 'HOST_NAME')

            self.resource_lock = threading.RLock()

            self.ntf_reader = notification.parser.NotificationParser(self.this_node, conf)
            self.ntf_manager = notification.manager.NotificationManager(self.this_node, conf)

            self.construct_logger()

    def construct_logger(self):
        #global logger
        #global log_level
        #global log_file
        #global conf
        self.logger = logging.getLogger('nodechecker')
        log_file_path = os.path.join(self.conf.hm_root, self.conf.nodechecker_home, self.log_file)
        handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=self.MAX_BYTES_LOGFILE, backupCount=5)
        if self.log_level == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] "
                                      " [%(funcName)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)