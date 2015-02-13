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

        RepeatingThreadSafeTimer.__init__(self,
                                          self._ctx.resource_lock,
                                          interval,
                                          util.send,
                                          [self._ctx.this_node,
                                           self._ctx.node_list,
                                           self._ctx.this_node.to_json()],
                                          kwargs)


class DeadNodeScanner(RepeatingThreadSafeTimer):
    def __init__(self, ctx, args=[], kwargs={}):
        self._node_creation_verifier_list = []
        self._ctx = ctx
        RepeatingThreadSafeTimer.__init__(self,
                                          self._ctx.resource_lock,
                                          self._ctx.dead_node_timeout,
                                          self._dead_node_scan, args, kwargs)

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

    def cancel(self):
        if self._node_creation_verifier_list:
            for t in self._node_creation_verifier_list:
                t.cancel()
            self._node_creation_verifier_list[:] = []

        self.finished.set()
        return self._node_creation_verifier_list

    def _remove_expired_timers(self):
        for timer in self._node_creation_verifier_list:
            if not timer.isAlive:
                self._node_creation_verifier_list.remove(timer)

    def _node_state(self, node_dir, at_time, known_as_dead):
        self._ctx.min_time_diff = -1
        res = "NOT_CHANGED"
        if os.path.exists(node_dir):
            # os.path.walk() calls find_minimal_rrd_timestamp() on each rrd file,
            # and the latst update time from the rrd files is
            # stored as self._ctx.min_time_diff 
            os.path.walk(node_dir, self.find_minimal_rrd_timestamp, [at_time])
            diff = self._ctx.min_time_diff

            if diff >= self._ctx.dead_node_timeout and not known_as_dead:
                print("..6..")
                print (diff)
                # logger.debug("Found dead node %s" % n.hostname)
                # logger.debug(
                # "n.hostname = %s,dead_node_set=%s," \
                # " known_as_dead %s, diff = %s "
                #    % (n.hostname, self._ctx.dead_node_set, str(known_as_dead),
                #       diff))
                #found_new_dead_node = True
                res = "CHANGED_TO_DEAD"
                

            elif diff < self._ctx.dead_node_timeout and known_as_dead:
                print("..7..")
                # logger.debug("Found node that resurrected from dead: %s"
                # % n.hostname)
                # logger.debug(
                # "n.hostname = %s,dead_node_set=%s,known_as_dead %s," \
                #    " diff = %s "
                #    % (n.hostname, self._ctx.dead_node_set, str(known_as_dead),
                #       diff))
                #found_resurrected_node = True
                res = "CHANGED_TO_ALIVE"
        elif not known_as_dead:
            res = "CHANGED_TO_DEAD"
        else:
            #log
            print("WARNING unexpected state")    
        return res   
            
    def _dead_node_scan(self):
        dead_node_list = []
        resurrected_node_list = []

        self._remove_expired_timers()
        # self._ctx.resource_lock.acquire()
        try:
            
            # Go through nodes, and check if some node's state changed.
            # Add dead and reborn nodes to appropriate lists
            for n in self._ctx.node_list:
                if self._ctx.this_node.ip_address == n.ip_address:
                    print("---0---")
                    continue
                path = os.path.join(self._ctx.conf.hm_root, self._ctx.conf.collectd_home, self._ctx.conf.collectd_rrd_dir, n.hostname)
                node_state = "NOT_CHANGED"
            
                known_as_dead = n.ip_address in self._ctx.dead_node_set
                print("n.ip_address, self._ctx.dead_node_set:" + n.ip_address, self._ctx.dead_node_set)
                node_state = self._node_state(path, time.mktime(time.localtime()), known_as_dead)

                if node_state == "CHANGED_TO_DEAD":
                    print("---3---")
                    # logger.debug("new_dead_node_set:: %s" % self._ctx.new_dead_node_set)
                    if n.ip_address not in self._ctx.new_dead_node_set:
                        print("---4---")
                        # logger.info("Starting timer for new dead node")
                        self._ctx.new_dead_node_set.add(n.ip_address)
                        ncv = self._start_node_creation_verifier(n) 
                        self._node_creation_verifier_list.append(ncv) 
            
                if node_state == "CHANGED_TO_ALIVE":
                        print("---5---")
                        # logger.info("Found resurrected node, updating collections")
                        if self._process_node_resurrection(n):
                            print("---6---")
                            resurrected_node_list.append(n)
              
            # After checking node's state, process lists if needed                
            if dead_node_list:
                print("---7---")
                self._process_active_node_list_change()
                self._ctx.ntf_manager.process_node_status_alerts(
                        dead_node_list, "DEAD_NODE")
                            
            if resurrected_node_list:
                print("---8---")
                self._process_active_node_list_change()
                self._ctx.ntf_manager.process_node_status_alerts(
                    resurrected_node_list, "RESURRECTED_NODE")

        except:
            # _do_shutdown(sys.exc_info())
            pass
            print("EXCEPTION in dead_node_scan()" + str(sys.exc_info()))

        finally:
            pass
            #self._ctx.resource_lock.release()
    
    '''
    This function is written to ease up testing, for timer creation mocking
    '''
    def _start_node_creation_verifier(self, node):
        ncv = threading.Timer(self._ctx.NODE_CREATION_TIMEOUT, self.check_node_still_dead,[node])
        ncv.start()
        return ncv
    
                                                                         
    def _process_active_node_list_change(self):
        util.send(self._ctx.node_list, 
                  util.json_from_list(self._ctx.active_node_list, 'active_node_list'))
        util.store_list_to_file(self._ctx.active_node_list, 
                                self._ctx.active_node_list_file, 
                                self._ctx.this_node.group_name)
                                
    def check_node_still_dead(self, node):
        print(" enter check_node_still_dead")
        # global active_node_list
        # global new_dead_node_set
        # global dead_node_set
        # global min_time_diff

        # now = time.mktime(time.localtime())
        path = os.path.join(self.conf.hm_root, self._ctx.conf.collectd_home,
                            self._ctx.conf.collectd_rrd_dir,
                            node.hostname)
        self._ctx.resource_lock.acquire()
        try:
            self._ctx.min_time_diff = -1
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
        print("---enter---")

        time_now_in_ms = arg_list[0]
        # global min_time_diff
        for name in names:
            print("---0---")
            ##print(dir_name)
            #print(name)
            print(os.path.join(dir_name, name))
            filename = os.path.join(dir_name, name)
            if os.path.isfile(filename):
                print("---1---")

                pipe = subprocess.Popen(
                    ['rrdtool', 'last', filename], stdout=subprocess.PIPE)
                out = pipe.communicate()
                epoch = int(out[0])
                if epoch > 0:
                    print("---2---")

                    diff = time_now_in_ms - epoch
                    print ("diff:"  + str(diff))
                    if diff >=0:
                        if self._ctx.min_time_diff == -1:
                            print("---3---")
                            self._ctx.min_time_diff = diff
                        elif self._ctx.min_time_diff > diff:
                            print("---4--")
                            self._ctx.min_time_diff = diff
                else:
                    pass

