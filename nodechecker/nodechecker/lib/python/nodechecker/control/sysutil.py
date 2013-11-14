#!/usr/bin/env python2

import subprocess


def systemV_service_command(service, command):
    subprocess.Popen(['service', service, command])
