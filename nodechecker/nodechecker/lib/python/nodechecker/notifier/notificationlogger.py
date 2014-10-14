#!/usr/bin/env python2

import sys
import json
import logging.handlers
import notification
import nodechecker.util

OI_HEALTH_MONITORING_ROOT = "OI_HEALTH_MONITORING_ROOT"

class JsonWrapper(object):
    def __init__(self, node, notifications=None):
        self.node = node
        if notifications is None:
            notifications = []
        self.notifications = notifications

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if not (isinstance(obj, Notification)
                or isinstance(obj, Node)
                or isinstance(obj, JsonWrapper)):
            return super(JsonEncoder, self).default(obj)

        return obj.__dict__

class NotificationLogger(object):
    def __init__(self, config, node):
        self.logger = logging.getLogger('nodechecker.notificationlogger')
        self.node = node
        self.config = config
        self.ntf_logger = self.configure_logger()

def process_notifications(self, notification_list):
        if notification_list:
            try:
                log = json.dumps(JsonWrapper(self.node, notification_list),
                                cls=JsonEncoder)
                self.ntf_logger.info(log)
            except:
                nodechecker.util.log_exception(sys.exc_info())

    def configure_logger(self):
        logger = logging.getLogger('notifications')
        handler = logging.handlers.RotatingFileHandler(
            self.config.notifications_log_file,
            maxBytes=self.config.notifications_log_file_max_bytes,
            backupCount = self.config.notifications_log_file_backup_count)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger