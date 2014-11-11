import os
import inspect
import threading
import sys
import socket
import nodechecker.config
import nodechecker.node
import nodechecker.worker
import nodechecker.context
import nodechecker.timer
import nodechecker.udp_listener
from mock import MagicMock
import time


conf = None
runtime = None
resource_lock = None
ctx = None


def setup():
    global resource_lock, ctx
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    resource_lock = threading.RLock()
    this_node = nodechecker.node.Node()

    ctx = nodechecker.context.Context()
    ctx.this_node = this_node
    ctx.resource_lock = resource_lock


def test_send_receive_heartbeats():
    global resource_lock, ctx

    # Setup
    listener_node = nodechecker.node.Node(ip_address='5.5.5.5', port=11111)
    ctx2 = nodechecker.context.Context()
    ctx2.this_node = listener_node
    ctx2.resource_lock = resource_lock
    udp_listener = nodechecker.udp_listener.UDPSocketListener(ctx2)
    

    #worker = nodechecker.worker.Worker(ctx)
    n1 = nodechecker.node.Node(ip_address='127.0.0.1', port=11111)
    n2 = nodechecker.node.Node(ip_address='2.2.2.2', port=11911)
    n3 = nodechecker.node.Node(ip_address='3.3.3.3', port=11911)
    ctx.this_node = nodechecker.node.Node(ip_address='4.4.4.4', port=11911)
    ctx.node_list = [n1, n2, n3, ctx.this_node]

    t2 = nodechecker.timer.RepeatingTimer(2, send, [ctx.node_list, ctx.this_node.to_json()]) 

    # Run
    udp_listener.start()
    t2.start()
    
    time.sleep(5)

    t2.shutdown()        
    # Verification

    #time.sleep(1)
    print("*****awake, shutting down udp_listener")
    udp_listener.shutdown()
    udp_listener.join()
    assert udp_listener.isAlive() is False


def send(to_nodes, data):
        print("ENTER _send()")
        try:
            if len(to_nodes) > 0:
                #self._logger.debug("Sending data %s" % str(data))
                print("Sending data:"  + str(data))

                for n in to_nodes:
                    if n != ctx.this_node:
                        ##self._logger.debug("Sending to node %s" % str(n.ip_address))
                        print("Sending to node:" + str(n.ip_address))
                        print("Sending to port:" + str(n.port))
                        

                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(data, (n.ip_address, n.port))
            else:
                #"self._do_shutdown()(None, 1, "No nodes to send data")
                pass
        except:
            print(sys.exc_info())
            #util.log_exception(sys.exc_info())


