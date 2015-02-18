#
# Default pound.cfg
#
# Pound listens on port 80 for HTTP and port 443 for HTTPS
# and distributes requests to 2 backends running on localhost.
# see pound(8) for configuration directives.
# You can enable/disable backends with poundctl(8).
#

User "pound"
Group "pound"
Control "/var/lib/pound/pound.cfg"

ListenHTTP
    Address OWN_IP
    Port OWN_PORT
End

#ListenHTTPS
#    Address 0.0.0.0
#    Port    443
#    Cert    "/etc/pki/tls/certs/pound.pem"
#End

Service
    BackEnd
        Address SERVER_IP
        Port SERVER_PORT
    End
    
#BackEnd
#    Address 127.0.0.1
#    Port    8001
#End
End
