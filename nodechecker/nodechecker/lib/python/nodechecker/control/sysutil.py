#!/usr/bin/env python2

import subprocess

def system_v_service_command(service, command):
    subprocess.Popen(['service', service, command])
