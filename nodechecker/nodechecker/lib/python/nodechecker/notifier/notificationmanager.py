#!/usr/bin/env python2

import os
import sys

import mailsender
import notificationlogger
import notification
import nodechecker.util

ENV_HM_HOME_DIR = "OI_HEALTH_MONITORING_ROOT"

class NotificationManager(object):
    def __init__(self, node, conf):
        self.conf = conf
        self.node = node
        self.mail_sender = self.create_mail_sender()
        self.notification_logger = notificationlogger.\
                NotificationLogger(self.conf, self.node)

    def process_notifications(self, notification_list):
        self.notification_logger.log(notification_list)
        if self.mail_sender is not None:
            self.mail_sender.send(notification_list)
        self.move_processed_notifications(notification_list)

    def process_node_status_alerts(self, node_list, category):
        self.process_notifications(self.create_notifications(
                node_list, category))

        # if self.notification_logger:
        #     self.notification_logger.process_node_status_alerts(node_list, category)
        # if self.mail_sender:
        #     self.mail_sender.process_node_status_alerts(node_list, category)
        # self.move_sent_items(notification_list)

    def create_mail_sender(self, node):
        if self.conf.email_use == 'yes':
            return mailsender.MailSender(self.conf, self.node)
        return None

    def move_processed_notifications(self, notification_list):
        try:
            for n in notification_list:
                if n.file_path:
                    os.rename(n.file_path, os.path.join(
                        os.environ[ENV_HM_HOME_DIR],
                        self.conf.notifications_home_dir,
                        self.conf.notifications_sent_dir,
                        n.file_name))
                else:
                    pass
        except:
            nodechecker.util.log_exception(sys.exc_info())

    def create_notifications(self, node_list, category):
        notification_list = []
        try:
            for n in node_list:
                new_notification = notification.Notification()
                notification_list.append(
                    new_notification.from_node(n, category))
            #self.send_notifications(notification_list)
        except:
            nodechecker.util.log_exception(sys.exc_info())
        return notification_list