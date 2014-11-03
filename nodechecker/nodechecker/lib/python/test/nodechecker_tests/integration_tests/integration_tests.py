
import os
import shutil
import inspect
import nodechecker.notification.notification
import nodechecker.notification.snmp
import nodechecker.config
import nodechecker.node
import nodechecker.nodechecker

node = None
conf = None
sender = None
test_dir = None


def setup():
    global node, conf, sender, test_dir
    node = nodechecker.node.Node(hostname='test1', port=10, cloud_zone='cloudzone1', ip_address_public='1.2.3.4',
                                     instance_id=1, cluster_id=1, machine_id=1)

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    conf = nodechecker.config.Config(os.path.join(test_dir, 'nodechecker.conf'))

    # prepare test environment
    install_dir = os.path.join(test_dir, 'install_dir')

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
        shutil.copytree(var_dir, os.path.join(install_dir, 'var'))
    except:
        pass

def teardown():
    #shutil.rmtree(os.path.join(test_dir, 'install_dir', 'var'))
    pass

def test():
    assert 1 == 1
    nodechecker.nodechecker.main()

