class Context(object):

    # Constants
    BIG_TIME_DIFF = 1000000
    RRD_HTTP_SERVER_PORT = 8181
    NODE_CREATION_TIMEOUT = 500
    MAX_BYTES_LOGFILE = 5000000
    MAX_CMT_CONF_WAIT = 600
    CMT_CONF_WAIT = 10

    # Runtime collections
    node_list = []
    active_node_list = []
    dead_node_set = set()
    new_dead_node_set = set()
    master_list = []

    # Runtime classes
    heartbeat_timer = None
    udp_listener = None
    ntf_reader = None
    nodelist_reader = None
    ntf_manager = None
    node_manager = None
    conf = None
    this_node = None
    dead_node_timer = None
    delayed_dead_node_timer = None
    logger = None
    resource_lock = None

    # State variables
    role = "SLAVE"
    mode = "RUN"
    my_master = None

    # Configuration variables
    heartbeat_period = 1
    rrd_scan_period = 1
    dead_node_timeout = 1
    heartbeats_received = 0
    min_time_diff = BIG_TIME_DIFF
    log_level = ""
    log_file = ""
    node_list_file = ""
    active_node_list_file = ""