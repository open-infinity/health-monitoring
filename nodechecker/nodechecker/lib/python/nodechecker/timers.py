import subprocess
import sys
import threading
import socket
import time
import os
import util


# Thread for sending heartbeats
def timer_heartbeat_start(ctx):
    # global timer_heartbeat
    ctx.resource_lock.acquire()
    print("ENTER send_heartbeats()")
    try:
        send(ctx.this_node, ctx.node_list, ctx.this_node.to_json())
        ctx.timer_heartbeat = threading.Timer(ctx.heartbeat_period, timer_heartbeat_start, [ctx])
        ctx.timer_heartbeat.start()
    except:
        util.log_exception(sys.exc_info())
    finally:
        ctx.resource_lock.release()


# Thread thread for dead node scanning
def timer_dead_node_scan_start(ctx):
    # global dead_node_timer
    dead_node_scan(ctx)
    ctx.timer_dead_node = threading.Timer(
        ctx.rrd_scan_period, timer_dead_node_scan_start, [ctx])
    ctx.timer_dead_node.start()


# Thread thread for checking if the dead node is still dead after period
def timer_delayed_dead_node_start(n, ctx):
    ctx.delayed_dead_node_timer = threading.Timer(ctx.NODE_CREATION_TIMEOUT,
                                              check_node_still_dead,
                                              [n, ctx])
    ctx.delayed_dead_node_timer.start()


def cancel(ctx):
        print("ENTER _cancel_timers")
        #global timer_heartbeat
        #global dead_node_timer
        #global delayed_dead_node_timer

        if ctx.timer_heartbeat:
            print("_ctx.timer_heartbeat.cancel()")
            print(ctx.timer_heartbeat.is)
            ctx.timer_heartbeat.cancel()

        if ctx.timer_dead_node:
            print("_ctx.timer_dead_node.cancel()")
            ctx.timer_dead_node.cancel()
        if ctx.timer_delayed_dead_node:
            print("_ctx.timer_delayed_dead_node.cancel()")
            ctx.timer_delayed_dead_node.cancel()

def send(this_node, to_nodes, data):
    # def send(ctx):
    time.sleep(10)
    print("ENTER send()")
    try:
        if len(to_nodes) > 0:
            # _#logger.debug("Sending data %s" % str(data))
            print("Sending data:" + str(data))

            for n in to_nodes:
                if n != this_node:
                    # _#logger.debug("Sending to node %s" % str(n.ip_address))
                    print("Sending to node:" + str(n.ip_address))
                    print("Sending to port:" + str(n.port))

                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(data, (n.ip_address, n.port))
        else:
            # _do_shutdown()(None, 1, "No nodes to send data")
            pass
    except:
        print("EXCEPTION in send() " + sys.exc_info())
        util.log_exception(sys.exc_info())


def dead_node_scan(ctx):
    # global min_time_diff
    # global new_dead_node_set
    # global delayed_dead_node_timer

    dead_node_list = []
    resurrected_node_list = []

    #now = time.mktime(time.localtime())
    ctx.resource_lock.acquire()
    try:
        for n in ctx.node_list:
            if ctx.this_node.ip_address == n.ip_address:
                continue
            found_new_dead_node = False
            found_resurrected_node = False
            path = os.path.join(ctx.conf.collectd_home, ctx.conf.collectd_rrd_dir, n.hostname)
            known_as_dead = n.ip_address in ctx.dead_node_set
            #FIXME: Nested try
            try:
                ctx.min_time_diff = ctx.BIG_TIME_DIFF
                #TODO: newest = max(glob.iglob('upload/*.log'), key=os.path.getctime)
                os.path.walk(path, find_minimal_rrd_timestamp, [ctx, time.mktime(time.localtime())])
                diff = ctx.min_time_diff

                if diff >= ctx.dead_node_timeout and not known_as_dead:
                    #logger.debug("Found dead node %s" % n.hostname)
                    #logger.debug(
                    #    "n.hostname = %s,dead_node_set=%s," \
                    #    " known_as_dead %s, diff = %s "
                    #    % (n.hostname, ctx.dead_node_set, str(known_as_dead),
                    #       diff))
                    found_new_dead_node = True

                elif diff < ctx.dead_node_timeout and known_as_dead:
                    #logger.debug("Found node that resurrected from dead: %s"
                    #% n.hostname)
                    #logger.debug(
                    #    "n.hostname = %s,dead_node_set=%s,known_as_dead %s," \
                    #    " diff = %s "
                    #    % (n.hostname, ctx.dead_node_set, str(known_as_dead),
                    #       diff))
                    found_resurrected_node = True

            except os.error:
                # TODO: don't use exceptions for program flow
                found_new_dead_node = True

            except:
                #_do_shutdown(sys.exc_info())
                pass
                print("EXCEPTION 2 in dead_node_scan" + sys.exc_info())

            finally:
                if found_new_dead_node:
                    #logger.debug("new_dead_node_set:: %s" % ctx.new_dead_node_set)
                    if n.ip_address not in ctx.new_dead_node_set:
                        #logger.info("Starting timer for new dead node")
                        ctx.new_dead_node_set.add(n.ip_address)
                        #delayed_dead_node_timer = threading.Timer(
                        #    ctx.NODE_CREATION_TIMEOUT,
                        #    functools.partial(check_node_still_dead, n))


                        timer_delayed_dead_node_start(n, ctx)
                        #delayed_dead_node_timer = threading.Timer(ctx.NODE_CREATION_TIMEOUT,
                        #                                          check_node_still_dead,
                        #                                          [n, ctx])
                        #delayed_dead_node_timer.start()
                if found_resurrected_node:
                    #logger.info("Found resurrected node, updating collections")
                    #if process_node_resurrection(
                    #        n, ctx.active_node_list, ctx.dead_node_set):
                    if process_node_resurrection(n, ctx):
                        resurrected_node_list.append(n)

        if dead_node_list or resurrected_node_list:
            send(ctx.node_list, util.json_from_list(
                ctx.active_node_list, 'active_node_list'))
            util.store_list_to_file(
                ctx.active_node_list, ctx.active_node_list_file, ctx.this_node.group_name)

            if resurrected_node_list:
                #mail_sender.send_node_status_alerts(
                #     resurrected_node_list, "RESURRECTED_NODE")
                ctx.ntf_manager.process_node_status_alerts(
                    resurrected_node_list, "RESURRECTED_NODE")

            if dead_node_list:
                #mail_sender.send_node_status_alerts(
                #     dead_node_list, "DEAD_NODE")
                ctx.ntf_manager.process_node_status_alerts(
                    dead_node_list, "DEAD_NODE")

    except:
        #_do_shutdown(sys.exc_info())
        pass
        print("EXCEPTION in dead_node_scan()" + sys.exc_info())

    finally:
        ctx.resource_lock.release()

    return dead_node_list


def check_node_still_dead(node, ctx):
    # global active_node_list
    # global new_dead_node_set
    #global dead_node_set
    #global min_time_diff

    #now = time.mktime(time.localtime())
    path = os.path.join(ctx.conf.collectd_home, ctx.conf.collectd_rrd_dir,
                        node.hostname)
    ctx.resource_lock.acquire()
    try:
        ctx.min_time_diff = ctx.BIG_TIME_DIFF
        os.path.walk(path, find_minimal_rrd_timestamp, [ctx, time.mktime(time.localtime())])
        diff = ctx.min_time_diff
        if diff < ctx.dead_node_timeout:
            pass
        else:
            ctx.active_node_list.remove(node)
            ctx.dead_node_set.add(node.ip_address)
            ctx.send(ctx.node_list, util.json_from_list(
                ctx.active_node_list, 'active_node_list'))
            ctx.ntf_manager.process_node_status_alerts([node], "DEAD_NODE")
            util.store_list_to_file(
                ctx.active_node_list, ctx.active_node_list_file, ctx.this_node.group_name)
        ctx.new_dead_node_set.remove(node.ip_address)
    except:
        #util.log_exception(sys.exc_info())
        print(" EXCEPTION in check_node_still_dead" + str(sys.exc_info()))
        pass
    finally:
        ctx.resource_lock.release()


# TODO: newest = max(glob.iglob('upload/*.log'), key=os.path.getctime)
def find_minimal_rrd_timestamp(arg_list, dir_name, names):
    ctx = arg_list[0]
    time_now_in_ms = arg_list[1]
    # global min_time_diff
    for name in names:
        filename = os.path.join(dir_name, name)
        if os.path.isfile(filename):
            pipe = subprocess.Popen(
                ['rrdtool', 'last', filename], stdout=subprocess.PIPE)
            out = pipe.communicate()
            epoch = int(out[0])
            if epoch > 0:
                diff = time_now_in_ms - epoch
                if ctx.min_time_diff > diff:
                    ctx.min_time_diff = diff
            else:
                pass


# def process_node_resurrection(resurrected_node, active_nodes, dead_nodes):
def process_node_resurrection(node, ctx):
    if node in ctx.node_list:
        ctx.active_nodes.append(ctx.resurrected_node)
        ctx.dead_node_set.remove(node.ip_address)
        return True
    else:
        return False