#!/usr/bin/env python2

import sys
import os
import json
import logging.handlers
import notification
import nodechecker.util
import nodechecker.node


class JsonWrapper(object):
    def __init__(self, node, notifications=None):
        self.node = node
        if notifications is None:
            notifications = []
        self.notifications = notifications

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if not (isinstance(obj, notification.Notification)
                or isinstance(obj, nodechecker.node.Node)
                or isinstance(obj, JsonWrapper)):
            return super(JsonEncoder, self).default(obj)

        return obj.__dict__

class NotificationLogger(object):
    def __init__(self, config, node):
        self.node = node
        self.conf = config
        self.logger = logging.getLogger('nodechecker.notificationlogger')
        self.ntf_logger = self.configure_logger()

    def log(self, notification_list):
        if notification_list:
            try:
                dump = json.dumps(JsonWrapper(self.node, notification_list),
                                cls=JsonEncoder)
                self.ntf_logger.info(dump)
            except:
                nodechecker.util.log_exception(sys.exc_info())

    def configure_logger(self):
        logger = logging.getLogger('notifications')
        handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.conf.hm_root, self.conf.nodechecker_home, self.conf.notifications_log_file),
            maxBytes=self.conf.notifications_log_file_max_bytes,
            backupCount=self.conf.notifications_log_file_backup_count)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
