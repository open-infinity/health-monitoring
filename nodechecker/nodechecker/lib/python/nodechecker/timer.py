import subprocess
import sys
import threading
import time
import os

import util


class RepeatingThreadSafeTimer(threading.Thread):
    def __init__(self, r_lock, interval, function, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.r_lock = r_lock
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()

    def run(self):
        while True:
            now = time.strftime("%H:%M:%S:%MS", time.localtime())
            print(now + "...timer waiting" )

            self.finished.wait(self.interval)

            now = time.strftime("%H:%M:%S:%MS", time.localtime())
            print(now + "...timer awake")
            if not self.finished.is_set():
                now = time.strftime("%H:%M:%S:%MS", time.localtime())
                print(now + "...executing function")
                self.r_lock.acquire()
                try:
                    self.function(*self.args, **self.kwargs)
                except:
                    pass
                finally:
                    self.r_lock.release()
                now = time.strftime("%H:%M:%S:%MS", time.localtime())
                print(now + "...function done")
            else:
                print("finished is set")
                break
            print ("RepeatingThreadSafeTimer EXIT run ")

    def cancel(self):
        # print("..........finished")
        self.finished.set()


class HeartBeatSender(RepeatingThreadSafeTimer):
    def __init__(self, interval, args=[], kwargs={}):
        self._ctx = args[0]

        RepeatingThreadSafeTimer.__init__(self, self._ctx.resource_lock, interval,
                                          util.send,
                                          [self._ctx.this_node,
                                           self._ctx.node_list,
                                           self._ctx.this_node.to_json()],
                                          kwargs)


class DeadNodeScanner(RepeatingThreadSafeTimer):
    def __init__(self, interval, ctx, args=[], kwargs={}):
        self._nodeCreationVerifier = None
        self._ctx = ctx
        self._ctx.blah = None
        RepeatingThreadSafeTimer.__init__(self, self._ctx.resource_lock, interval,
                                          self.blah, args, kwargs)

    # def process_node_resurrection(resurrected_node, active_nodes, dead_nodes):
    # TODO: change node uuid everwhere to ip+port
    # This means sets with host names has to be replaced with lists with full objects perhaps
    def _process_node_resurrection(self, node):
        if node in self._ctx.node_list:
            self._ctx.active_nodes.append(self._ctx.resurrected_node)
            self._ctx.dead_node_set.remove(node.ip_address)

            return True
        else:
            return False

    def run(self):
        while True:
            print("overriden run")
            now = time.strftime("%H:%M:%S:%MS", time.localtime())
            print(now + "...timer waiting" )

            self.finished.wait(self.interval)

            now = time.strftime("%H:%M:%S:%MS", time.localtime())
            print(now + "...timer awake")
            if not self.finished.is_set():
                now = time.strftime("%H:%M:%S:%MS", time.localtime())
                print(now + "...executing function")
                self.r_lock.acquire()
                try:
                    self.function(*self.args, **self.kwargs)
                except:
                    pass
                finally:
                    self.r_lock.release()
                now = time.strftime("%H:%M:%S:%MS", time.localtime())
                print(now + "...function done")
            else:
                print("finished is set")
                #self._nodeCreationVerifier.cancel()
                break
            print ("RepeatingThreadSafeTimer EXIT run ")

    def cancel(self):
        print("..........overridded cancel")

        if self._nodeCreationVerifier:
            print("cancelling _nodeCreationVerifier")
            self._nodeCreationVerifier.cancel()
            print("waiting for termination of _nodeCreationVerifier")
            self._nodeCreationVerifier.join()
            #time.sleep(5)

        self.finished.set()
        print("cancel exit")

    def blah(self):
        print("blaaaaaaaaaaaaaaaaaaaaaaah")
        dead_node_list = []
        resurrected_node_list = []

        try:
            for n in self._ctx.node_list:
                #if self._nodeCreationVerifier:
                #    self._nodeCreationVerifier.cancel()
                print("..1..")
                if self._ctx.this_node.ip_address == n.ip_address:
                    print("..2..")
                    continue
                print("..3..")
                found_new_dead_node = False
                found_resurrected_node = False
                path = os.path.join(self._ctx.conf.collectd_home, self._ctx.conf.collectd_rrd_dir, n.hostname)
                known_as_dead = n.ip_address in self._ctx.dead_node_set
                # FIXME: Nested try
                try:
                    self._ctx.min_time_diff = self._ctx.BIG_TIME_DIFF
                    os.path.walk(path, self.find_minimal_rrd_timestamp,
                                 [self._ctx, time.mktime(time.localtime())])
                    diff = self._ctx.min_time_diff
                    print("..5..")

                    if diff >= self._ctx.dead_node_timeout and not known_as_dead:
                        print("..6..")
                        found_new_dead_node = True

                    elif diff < self._ctx.dead_node_timeout and known_as_dead:
                        print("..7..")
                        found_resurrected_node = True

                except os.error:
                    # TODO: don't use exceptions for program flow
                    print("..8..")
                    found_new_dead_node = True

                except:
                    print("..9..")
                    pass
                    print("EXCEPTION 2 in dead_node_scan" + str(sys.exc_info()))

                finally:
                    if found_new_dead_node:
                        print("..10..")
                        if n.ip_address not in self._ctx.new_dead_node_set:
                            print("..11..")
                            self._ctx.new_dead_node_set.add(n.ip_address)
                            #self._nodeCreationVerifier = threading.Timer(self._ctx.NODE_CREATION_TIMEOUT,
                            #                                             self.check_node_still_dead,
                            #                                             [n])
                            #self._nodeCreationVerifier.start()
                            self._ctx.blah = threading.Timer(self._ctx.NODE_CREATION_TIMEOUT,
                                                                         self.check_node_still_dead,
                                                                         [n])
                            self._ctx.blah.start()
                            time.sleep(6)
                            self._ctx.blah.cancel()
                    if found_resurrected_node:
                        print("..12..")
                        if self._process_node_resurrection(n):
                            resurrected_node_list.append(n)
                    #self._nodeCreationVerifier.cancel()
                print("canceliing")
                self._ctx.blah.cancel()
                print("canceliing")

            print("..13..")
            #self._nodeCreationVerifier.cancel()
            if dead_node_list or resurrected_node_list:
                print("..14..")
                util.send(self._ctx.node_list, util.json_from_list(
                    self._ctx.active_node_list, 'active_node_list'))
                util.store_list_to_file(
                    self._ctx.active_node_list, self._ctx.active_node_list_file, self._ctx.this_node.group_name)

                if resurrected_node_list:
                    print("..15..")
                    self._ctx.ntf_manager.process_node_status_alerts(
                        resurrected_node_list, "RESURRECTED_NODE")

                if dead_node_list:
                    print("..16..")
                    self._ctx.ntf_manager.process_node_status_alerts(
                        dead_node_list, "DEAD_NODE")

        except:
            print("..17..")
            pass
            print("EXCEPTION in dead_node_scan()" + str(sys.exc_info()))

        finally:
            print("..18..")
            self._nodeCreationVerifier.cancel()
            pass

    def _dead_node_scan(self):
        dead_node_list = []
        resurrected_node_list = []

        # self._ctx.resource_lock.acquire()
        try:
            for n in self._ctx.node_list:
                print("..1..")
                if self._ctx.this_node.ip_address == n.ip_address:
                    print("..2..")
                    continue
                print("..3..")
                found_new_dead_node = False
                found_resurrected_node = False
                #print(self._ctx.conf.collectd_home)
                #print(self._ctx.conf.collectd_rrd_dir)
                path = os.path.join(self._ctx.conf.collectd_home, self._ctx.conf.collectd_rrd_dir, n.hostname)
                #print("..3.1.")
                known_as_dead = n.ip_address in self._ctx.dead_node_set

                #print("..4..")
                # FIXME: Nested try
                try:
                    self._ctx.min_time_diff = self._ctx.BIG_TIME_DIFF
                    # TODO: newest = max(glob.iglob('upload/*.log'), key=os.path.getctime)
                    os.path.walk(path, self.find_minimal_rrd_timestamp,
                                 [self._ctx, time.mktime(time.localtime())])
                    diff = self._ctx.min_time_diff
                    print("..5..")

                    if diff >= self._ctx.dead_node_timeout and not known_as_dead:
                        print("..6..")
                        # logger.debug("Found dead node %s" % n.hostname)
                        # logger.debug(
                        # "n.hostname = %s,dead_node_set=%s," \
                        # " known_as_dead %s, diff = %s "
                        #    % (n.hostname, self._ctx.dead_node_set, str(known_as_dead),
                        #       diff))
                        found_new_dead_node = True

                    elif diff < self._ctx.dead_node_timeout and known_as_dead:
                        print("..7..")
                        # logger.debug("Found node that resurrected from dead: %s"
                        # % n.hostname)
                        # logger.debug(
                        # "n.hostname = %s,dead_node_set=%s,known_as_dead %s," \
                        #    " diff = %s "
                        #    % (n.hostname, self._ctx.dead_node_set, str(known_as_dead),
                        #       diff))
                        found_resurrected_node = True

                except os.error:
                    # TODO: don't use exceptions for program flow
                    print("..8..")
                    found_new_dead_node = True

                except:
                    # _do_shutdown(sys.exc_info())
                    print("..9..")
                    pass
                    print("EXCEPTION 2 in dead_node_scan" + str(sys.exc_info()))

                finally:
                    if found_new_dead_node:
                        print("..10..")
                        # logger.debug("new_dead_node_set:: %s" % self._ctx.new_dead_node_set)
                        if n.ip_address not in self._ctx.new_dead_node_set:
                            print("..11..")
                            # logger.info("Starting timer for new dead node")
                            self._ctx.new_dead_node_set.add(n.ip_address)
                            # delayed_dead_node_timer = threading.Timer(
                            # self._ctx.NODE_CREATION_TIMEOUT,
                            # functools.partial(check_node_still_dead, n))

                            #timer_delayed_dead_node_start(n, self._ctx)
                            #self._nodeCreationVerifier = threading.Timer(self._ctx.NODE_CREATION_TIMEOUT,
                            #                                             self.check_node_still_dead,
                            #                                             [n])
                            #self._nodeCreationVerifier.start()
                    if found_resurrected_node:
                        print("..12..")
                        # logger.info("Found resurrected node, updating collections")
                        # if process_node_resurrection(
                        # n, self._ctx.active_node_list, self._ctx.dead_node_set):
                        if self._process_node_resurrection(n):
                            resurrected_node_list.append(n)
            print("..13..")
            if dead_node_list or resurrected_node_list:
                print("..14..")
                util.send(self._ctx.node_list, util.json_from_list(
                    self._ctx.active_node_list, 'active_node_list'))
                util.store_list_to_file(
                    self._ctx.active_node_list, self._ctx.active_node_list_file, self._ctx.this_node.group_name)

                if resurrected_node_list:
                    print("..15..")
                    # mail_sender.send_node_status_alerts(
                    # resurrected_node_list, "RESURRECTED_NODE")
                    self._ctx.ntf_manager.process_node_status_alerts(
                        resurrected_node_list, "RESURRECTED_NODE")

                if dead_node_list:
                    print("..16..")
                    # mail_sender.send_node_status_alerts(
                    # dead_node_list, "DEAD_NODE")
                    self._ctx.ntf_manager.process_node_status_alerts(
                        dead_node_list, "DEAD_NODE")

        except:
            print("..17..")
            # _do_shutdown(sys.exc_info())
            pass
            print("EXCEPTION in dead_node_scan()" + str(sys.exc_info()))

        finally:
            print("..18..")
            pass
            #self._ctx.resource_lock.release()
            # return dead_node_list

    def check_node_still_dead(self, node):
        print(" enter check_node_still_dead")
        # global active_node_list
        # global new_dead_node_set
        # global dead_node_set
        # global min_time_diff

        # now = time.mktime(time.localtime())
        path = os.path.join(self._ctx.conf.collectd_home, self._ctx.conf.collectd_rrd_dir,
                            node.hostname)
        self._ctx.resource_lock.acquire()
        try:
            self._ctx.min_time_diff = self._ctx.BIG_TIME_DIFF
            os.path.walk(path, self.find_minimal_rrd_timestamp, [time.mktime(time.localtime())])
            diff = self._ctx.min_time_diff
            if diff < self._ctx.dead_node_timeout:
                pass
            else:
                if node in self._ctx.active_node_list:
                    self._ctx.active_node_list.remove(node)
                else:
                    print("this is strange")
                self._ctx.dead_node_set.add(node.ip_address)
                util.send(self._ctx.this_node,
                          self._ctx.node_list,
                          util.json_from_list(
                              self._ctx.active_node_list, 'active_node_list'))
                self._ctx.ntf_manager.process_node_status_alerts([node], "DEAD_NODE")
                util.store_list_to_file(
                    self._ctx.active_node_list, self._ctx.active_node_list_file, self._ctx.this_node.group_name)
            self._ctx.new_dead_node_set.remove(node.ip_address)
        except:
            # util.log_exception(sys.exc_info())
            print(" EXCEPTION in check_node_still_dead" + str(sys.exc_info()))
            pass
        finally:
            self._ctx.resource_lock.release()
        print(" exit check_node_still_dead")


    # TODO: newest = max(glob.iglob('upload/*.log'), key=os.path.getctime)
    def find_minimal_rrd_timestamp(self, arg_list, dir_name, names):
        # ctx = arg_list[0]
        time_now_in_ms = arg_list[0]
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
                    if self._ctx.min_time_diff > diff:
                        self._ctx.min_time_diff = diff
                else:
                    pass