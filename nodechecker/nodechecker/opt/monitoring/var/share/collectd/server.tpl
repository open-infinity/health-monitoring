LoadPlugin rrdtool
LoadPlugin network

<Plugin rrdtool>
       DataDir "RRD_DATA_DIR"
#       CacheTimeout 120
#       CacheFlush   900
</Plugin>


<Plugin network>
#       # server setup:
       <Listen "LISTEN_IP" "25826">
#               SecurityLevel Sign
#               AuthFile "/etc/collectd/passwd"
#               Interface "eth0"
       </Listen>
</Plugin>


