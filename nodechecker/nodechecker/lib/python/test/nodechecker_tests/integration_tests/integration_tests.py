
import os
import sys
import shutil
import inspect
import nodechecker.notification.notification
import nodechecker.notification.snmp
import nodechecker.config
import nodechecker.node
import nodechecker.nodechecker
import nodechecker.control.servicemanager
import getpass

node = None
conf = None
sender = None
test_dir = None
user = getpass.getuser()


def setup():
    global node, conf, sender, test_dir
    
    node = nodechecker.node.Node(hostname='test1', port=10, cloud_zone='cloudzone1', ip_address_public='1.2.3.4',
                                     instance_id=1, cluster_id=1, machine_id=1)

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    print(test_dir)
    conf_file = os.path.join(test_dir, 'nodechecker.conf')
    conf = nodechecker.config.Config(conf_file)

    # setup healhmonitoring root and tree
    conf.hm_root = os.path.join(test_dir, 'hm_root')
    nodechecker_home = os.path.join(conf.hm_root, conf.nodechecker_home)
    collectd_home = os.path.join(conf.hm_root, conf.collectd_home)
    pound_home = os.path.join(conf.hm_root, conf.pound_home)
    rrd_http_server_home = os.path.join(conf.hm_root, conf.rrd_http_server_home)

    # traverse 5 levels up in directory tree, to nodechecker root dir
    # TODO: is there some search functcion available? implement one if not
    p1_dir = os.path.abspath(os.path.join(test_dir, os.pardir))
    p2_dir = os.path.abspath(os.path.join(p1_dir, os.pardir))
    p3_dir = os.path.abspath(os.path.join(p2_dir, os.pardir))
    p4_dir = os.path.abspath(os.path.join(p3_dir, os.pardir))
    src_dir = os.path.abspath(os.path.join(p4_dir, os.pardir))

    var_dir = os.path.join(src_dir, 'opt', 'monitoring', 'var')
    # todo: remove exception handling
    try:
        print(test_dir)

        shutil.copytree(var_dir, os.path.join(nodechecker_home, 'var'))
        os.makedirs(os.path.join(nodechecker_home, 'var', 'log'))
        os.makedirs(collectd_home)
        print(1)
        os.makedirs(pound_home)
        print(2)

        os.makedirs(rrd_http_server_home)
        print(3)
        # copy nodechecker.conf to hm_root/nodechecker/etc
        #data/hm_root/nodechecker/etc
        print(test_dir)
        etc_dir = os.path.join(test_dir, 'data', 'hm_root', 'nodechecker', 'etc')
        shutil.copytree(etc_dir, os.path.join(nodechecker_home, 'etc'))
        #shutil.copyfile(os.path.join(conf_from_dir, 'nodelist.conf'), os.path.join(nodechecker_home, 'etc', 'nodelist.conf'))
        #shutil.copyfile(os.path.join(conf_from_dir, 'active_nodelist.conf'), os.path.join(nodechecker_home, 'etc', 'active_nodelist.conf'))

        

        print('env ready')
    except:
        print(sys.exc_info())
        pass

def teardown():
    #shutil.rmtree(os.path.join(test_dir, 'hm_root'))
    pass

def test_start():
    print('enter')
    global conf, user
    assert 1 == 1
    #nodechecker.nodechecker.main()
    #service_manager = nodechecker.control.servicemanager.ServiceManager(conf, user=user)
    #service_manager.start_services()
    nodechecker.nodechecker.start(conf)

