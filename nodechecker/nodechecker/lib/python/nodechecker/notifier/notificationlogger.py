#!/usr/bin/env python2

import sys
import json
import logging.handlers
import notification
import nodechecker.util

OI_HEALTH_MONITORING_ROOT = "OI_HEALTH_MONITORING_ROOT"


class NotificationLogger(object):

    def __init__(self, node, config):
        self.logger = logging.getLogger('nodechecker.notificationlogger')
        self.ntf_logger = self.configure_logger()
        self.node = node
        self.config = config

    def process_notifications(self, notification_list):
        if notification_list:
            try:
                sender_json = json.dumps(self.node.__dict__)

                for n in notification_list:
                    self.logger.info(n)
                    #self.ntf_logger.info(n)
                    notifications_json =json.dumps()

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