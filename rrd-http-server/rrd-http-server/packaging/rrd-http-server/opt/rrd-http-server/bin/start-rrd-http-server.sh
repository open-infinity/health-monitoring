#!/bin/bash

USER=toas
PID_FILE=/var/run/rrd-http-server.pid
CP=$TOAS_RRD_HTTP_SERVER_ROOT/lib/java/rrd-http-server.jar
PROPERTIES='log_dir='$TOAS_RRD_HTTP_SERVER_ROOT/var/log/
JVM_OPTIONS='-Xss256k -Xmx20m -Xms16m -XX:PermSize=12m -XX:MaxPermSize=18m -XX:+CMSClassUnloadingEnabled -XX:+UseCompressedOops'

/usr/bin/jsvc -user $USER -D$PROPERTIES $JVM_OPTIONS -pidfile $PID_FILE  -cp $CP org.openinfinity.rrddatareader.http.RrdHttpServer

