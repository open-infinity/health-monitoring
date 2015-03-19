#!/usr/bin/env python2

import smtplib
import logging
import email.mime.text

ENV_HM_HOME_DIR = "OI_HEALTH_MONITORING_ROOT"
MSG_DELIMITER = '-----------------------------------------------' \
                '------------------'


class MailSender(object):
    def __init__(self, conf, node):
        self.conf = conf
        self.eol = "\n"
        self.delimiter = MSG_DELIMITER
        self.node = node
        self.logger = logging.getLogger('nodechecker.mailsender')
        self.logger.info('creating an instance of nodechecker.mailsender')

    def send(self, notification_list):
        if notification_list:
            # try:
            msg = email.mime.text.MIMEText(
                self.format_email_message(notification_list))
            msg['Subject'] = self.conf.email_subject
            # msg['From'] = self.conf.email_from
            msg['From'] = ''
            msg['To'] = self.conf.email_to
            s = smtplib.SMTP(self.conf.email_smtp_server, self.conf.email_smtp_port)

            # Retry if sending fails
            send_attempts = 0
            while send_attempts < 5:
                try:
                    s.login(self.conf.email_smtp_username, self.conf.email_smtp_password)
                    s.sendmail('', self.conf.email_to, msg.as_string())
                    break
                except:
                    send_attempts += 1
            s.quit()

    def format_email_message(self, notification_list):
        # Message header
        list_count = len(notification_list)
        if list_count > 1:
            notification_word = ' notifications'
        else:
            notification_word = ' notification'
        msg_header = "".join(['This mail contains ', str(list_count),
                                      notification_word, " sent from Health monitoring master node at:"])

        # Sender host information
        sender_info = [self.eol, self.eol,
                       "Cloud zone: ", self.node.cloud_zone, self.eol,
                       "Instance ID: ", self.node.instance_id, self.eol,
                       "Cluster ID: ", self.node.cluster_id, self.eol,
                       "Machine ID:", self.node.machine_id, self.eol,
                       "Hostname: ", self.node.hostname, self.eol,
                       "Public IP: ", self.node.ip_address_public]
        msg_sender_info = "".join(sender_info)

        # Create email message body
        i = 0
        msg_body_items = []
        for notification in notification_list:
            i += 1
            body = [self.eol,
                    self.eol,
                    self.delimiter, self.eol,
                    'NOTIFICATION ', str(i), self.eol, self.eol]
            if notification.severity:
                body += ["Severity: ", notification.severity, self.eol]
            if notification.category:
                body += ["Category: ", notification.category, self.eol]
            if notification.machine_id:
                body += ["Machine ID: ", notification.machine_id, self.eol]
            if notification.hostname:
                body += ["Hostname: ", notification.hostname, self.eol]
            if notification.ip_address_public:
                body += ["Public IP: ", notification.ip_address_public,
                         self.eol]
            if notification.time:
                body += ["Time (UTC): ", notification.time, self.eol, self.eol]
            if notification.message:
                body += ["Message: ", notification.message]
            msg_body_items += body
        msg_body = "".join(msg_body_items)
        return msg_header + msg_sender_info + msg_body
