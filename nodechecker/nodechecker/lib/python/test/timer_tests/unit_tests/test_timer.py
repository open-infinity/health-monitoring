import os
import threading
import time

import nodechecker.config
import nodechecker.node

import nodechecker.timer
import nodechecker.context
import nodechecker.timer
import nodechecker.udp_listener

from mock import MagicMock, inspect, Mock, patch


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global resource_lock, ctx
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock


def test_dead_node_scanner_start_stop_with_node_creation_verifiers():
    global resource_lock, ctx

    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='n4')
    ctx.node_list = [n1, n2, n3, ctx.this_node]

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    ctx.conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))
    ctx.NODE_CREATION_TIMEOUT = 10

    ctx.ntf_manager = MagicMock()
    ctx.dead_node_timeout = 0.01
    print(ctx.conf.collectd_rrd_dir)
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)

    dead_node_scanner.start()
    time.sleep(ctx.dead_node_timeout * 10)
    pending_timers_list = dead_node_scanner.cancel()
    dead_node_scanner.join()
    assert dead_node_scanner.isAlive() is False
    assert len(pending_timers_list) == 0
    
def test_dead_node_scanner_node_changed_to_dead():
    global resource_lock, ctx
    with patch('threading.Timer') as mock:
        curr_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
        n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
        n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
        ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='n4')
        ctx.node_list = [n1, n2, n3, ctx.this_node]    
        ctx.active_node_list = [n1, n2, n3, ctx.this_node]
        ctx.dead_node_set = None
        ctx.conf = nodechecker.config.Config(os.path.join(curr_dir, 'nodechecker.conf'))
        #ctx.conf.hm_root = os.path.join(curr_dir_parent_2, "data")
        ctx.dead_node_timeout = 10
        #rrd_data_path = os.path.join(ctx.conf.hm_root, ctx.conf.collectd_home, ctx.conf.collectd_rrd_dir, ctx.this_node.hostname)
        # <lastupdate>1416251047</lastupdate> <!-- 2014-11-17 21:04:07 EET -->
        #last_update = 1416251047
            
        dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)
        dead_node_scanner._node_state = MagicMock(return_value="CHANGED_TO_DEAD")
        '''
        with patch('threading.Timer') as mock:
        ...     instance = mock.return_value
        ...     instance.method.return_value = 'the result'
        ...     result = some_function()
        ...     assert result == 'the result'
        ''' 
        ctx.NODE_CREATION_TIMEOUT = 10

        #ctx.ntf_manager = MagicMock()
        #ctx.dead_node_timeout = 0.01
        #print(ctx.conf.collectd_rrd_dir)
        #dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)

        dead_node_scanner._dead_node_scan()
        
        #assert dead_node_scanner.isAlive() is False
        #assert len(pending_timers_list) == 0
        assert len(ctx.new_dead_node_set) == 1


def test_node_state():
    
    curr_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    curr_dir_parent_1 = os.path.abspath(os.path.join(curr_dir, os.pardir))
    curr_dir_parent_2 = os.path.abspath(os.path.join(curr_dir_parent_1, os.pardir))

    
    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111, hostname='n1')
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911, hostname='n2')
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911, hostname='n3')
    
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911, hostname='test-host')
    ctx.node_list = [n1, n2, n3, ctx.this_node]
    ctx.active_node_list = [n1, n2, n3, ctx.this_node]
    ctx.dead_node_set = None
    ctx.conf = nodechecker.config.Config(os.path.join(curr_dir, 'nodechecker.conf'))
    #ctx.conf.collectd_rrd_dir = os.path.join(curr_dir_parent_2, "data", "rrd")
    ctx.conf.hm_root = os.path.join(curr_dir_parent_2, "data")

    ctx.dead_node_timeout = 10
    
    #rrd_data_path = os.path.join(curr_dir_parent_2, "data", "rrd")
    rrd_data_path = os.path.join(ctx.conf.hm_root, ctx.conf.collectd_home, ctx.conf.collectd_rrd_dir, ctx.this_node.hostname)
    # <lastupdate>1416251047</lastupdate> <!-- 2014-11-17 21:04:07 EET -->
    last_update = 1416251047
    
    dead_node_scanner = nodechecker.timer.DeadNodeScanner(ctx)
    
    assert "CHANGED_TO_DEAD" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout + 1, False)    
    assert "NOT_CHANGED" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout + 1, True)
    assert "CHANGED_TO_ALIVE" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout - 1 , True)
    assert "NOT_CHANGED" == dead_node_scanner._node_state(rrd_data_path, last_update + ctx.dead_node_timeout - 1 , False)


def test_find_minimal_rrd_timestamp():
    curr_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    curr_dir_parent_1 = os.path.abspath(os.path.join(curr_dir, os.pardir))
    curr_dir_parent_2 = os.path.abspath(os.path.join(curr_dir_parent_1, os.pardir))
    
    last_update = 1416251047
    
    args = [last_update]
    dir_name = os.path.join(curr_dir_parent_2, "data", "collectd", "rrd","test-host","load")
    names = ["load.rrd"] 
    ctx.min_time_diff = -1
    scanner = nodechecker.timer.DeadNodeScanner(ctx)
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 0
    
    ctx.min_time_diff = 0
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 0
    
    ctx.min_time_diff = 1
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 0
    
    ctx.min_time_diff = 50
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 0
    
    args = [last_update + 1]
    scanner._ctx.min_time_diff = 2
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 1
    
    args = [last_update - 1]
    scanner._ctx.min_time_diff = 2
    scanner.find_minimal_rrd_timestamp(args, dir_name, names)    
    assert scanner._ctx.min_time_diff == 2
    
    
    
    
    
    
    
    
    
    
    
    
    
        
