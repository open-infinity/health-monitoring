LoadPlugin network
<Plugin network>
#       # client setup:
        <Server "SERVER_IP" "25826">
#               SecurityLevel Encrypt
#               Username "user"
#               Password "secret"
#               Interface "eth0"
        </Server>
#       TimeToLive "128"
#       MaxPacketSize 1024
#
#       # proxy setup (client and server as above):
#       Forward true
#
#       # statistics about the network plugin itself
#       ReportStats false
#
#       # "garbage collection"
#       CacheFlush 1800
</Plugin>
