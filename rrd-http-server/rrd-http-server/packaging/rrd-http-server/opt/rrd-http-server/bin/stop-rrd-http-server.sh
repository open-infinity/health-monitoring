#!/bin/bash

PID_FILE=/var/run/rrd-http-server.pid
CP=$TOAS_RRD_HTTP_SERVER_ROOT/lib/java/rrd-http-server.jar

/usr/bin/jsvc -stop -pidfile $PID_FILE  -cp $CP org.openinfinity.rrddatareader.http.RrdHttpServer

