package org.openinfinity.rrddatareader.http;

import org.apache.commons.daemon.Daemon;
import org.apache.commons.daemon.DaemonContext;
import org.apache.commons.daemon.DaemonInitException;
import org.openinfinity.rrddatareader.util.PropertiesReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RrdHttpServer implements Daemon {
    private static final Logger LOGGER = LoggerFactory.getLogger(RrdHttpServer.class);
    
    MonitoringHttpListener server = null;
    
    @Override
    public void destroy() {
        LOGGER.debug("RrdHttpServer::destroy()");
    }
    
    @Override
    public void init(DaemonContext arg0) throws DaemonInitException, Exception {
        LOGGER.debug("RrdHttpServer::init()");
        server = new MonitoringHttpListener();
    }
    
    @Override
    public void start() throws Exception {
        LOGGER.debug("RrdHttpServer::start()");
        int port = PropertiesReader.getInteger("defaultPort");
        server.run(port);
    }
    
    @Override
    public void stop() throws Exception {
        LOGGER.debug("RrdHttpServer::stop()");
    }

}
