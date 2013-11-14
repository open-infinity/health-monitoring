/*
 * #%L
 * Health Monitoring : RRD Data Reader
 * %%
 * Copyright (C) 2012 Tieto
 * %%
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * #L%
 */
package org.openinfinity.rrddatareader.http;

import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;

import org.jboss.netty.bootstrap.ServerBootstrap;
import org.jboss.netty.channel.ChannelHandlerContext;
import org.jboss.netty.channel.ChannelPipeline;
import org.jboss.netty.channel.ChannelPipelineFactory;
import org.jboss.netty.channel.Channels;
import org.jboss.netty.channel.ExceptionEvent;
import org.jboss.netty.channel.MessageEvent;
import org.jboss.netty.channel.SimpleChannelUpstreamHandler;
import org.jboss.netty.channel.socket.nio.NioServerSocketChannelFactory;
import org.jboss.netty.handler.codec.http.DefaultHttpResponse;
import org.jboss.netty.handler.codec.http.HttpChunkAggregator;
import org.jboss.netty.handler.codec.http.HttpContentCompressor;
import org.jboss.netty.handler.codec.http.HttpRequest;
import org.jboss.netty.handler.codec.http.HttpRequestDecoder;
import org.jboss.netty.handler.codec.http.HttpResponse;
import org.jboss.netty.handler.codec.http.HttpResponseEncoder;
import org.jboss.netty.handler.codec.http.HttpResponseStatus;
import org.jboss.netty.handler.codec.http.HttpVersion;
import org.jboss.netty.handler.codec.http.QueryStringDecoder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MonitoringHttpListener {

    private static final Logger LOGGER = LoggerFactory.getLogger(MonitoringHttpListener.class);

    public ServerBootstrap run(int port) {
        ServerBootstrap bootstrap =
                new ServerBootstrap(new NioServerSocketChannelFactory(Executors.newFixedThreadPool(4),
                        Executors.newCachedThreadPool()));
        bootstrap.setPipelineFactory(newPipelineFactory());
        bootstrap.bind(new InetSocketAddress(port));
        return bootstrap;
    }

    public ChannelPipelineFactory newPipelineFactory() {
        return new ChannelPipelineFactory() {
            @Override
            public ChannelPipeline getPipeline() throws Exception {
                ChannelPipeline pipeline = Channels.pipeline();
                pipeline.addLast("decoder", new HttpRequestDecoder());
                pipeline.addLast("aggregator", new HttpChunkAggregator(1048576));
                pipeline.addLast("encoder", new HttpResponseEncoder());
                pipeline.addLast("deflater", new HttpContentCompressor());
                pipeline.addLast("handler", newHandler());
                return pipeline;
            }
        };
    }

    public SimpleChannelUpstreamHandler newHandler() {
        return new SimpleChannelUpstreamHandler() {
            @Override
            public void messageReceived(ChannelHandlerContext ctx, MessageEvent e) throws Exception {
                HttpRequest request = (HttpRequest) e.getMessage();
                HttpResponse response = getResponse(request);
                response.setHeader("Content-Length", response.getContent().readableBytes());
                response.setHeader("Content-Type", "application/json");
                e.getChannel().write(response);
            }

            @Override
            public void exceptionCaught(ChannelHandlerContext ctx, ExceptionEvent e) throws Exception {
                LOGGER.error("Exception: ", e.getCause());
                e.getChannel().write(
                        new DefaultHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.INTERNAL_SERVER_ERROR));
                e.getChannel().close();
            }
        };
    }

    public HttpResponse getResponse(HttpRequest request) throws Exception {
        HttpResponse response = new DefaultHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.OK);
        QueryStringDecoder queryStringDecoder = new QueryStringDecoder(request.getUri());

        boolean isOk = false;
        for (Map.Entry<String, AbstractHandler> entry : HANDLERS.entrySet()) {
            if (isOk = queryStringDecoder.getPath().startsWith(entry.getKey())) {
                entry.getValue().handle(response, queryStringDecoder);
                break;
            }
        }
        if (!isOk) {
            return new DefaultHttpResponse(HttpVersion.HTTP_1_1, HttpResponseStatus.NOT_FOUND);
        }

        return response;
    }

    static Map<String, AbstractHandler> HANDLERS = new HashMap<String, AbstractHandler>();
    
    public MonitoringHttpListener(){
        //int port = PropertiesReader.getInteger("defaultPort");
        HANDLERS.put("/monitoring/hostlist", new HostListHandler());
        HANDLERS.put("/monitoring/metrictypes", new MetricTypesHandler());
        HANDLERS.put("/monitoring/metricnames", new MetricNamesHandler());
        HANDLERS.put("/monitoring/healthstatus", new HealthStatusHandler());
        HANDLERS.put("/monitoring/notifications", new NotificationHandler());
        HANDLERS.put("/monitoring/metricboundaries", new MetricBoundariesHandler());
        HANDLERS.put("/monitoring/grouplist", new GroupListHandler());
        HANDLERS.put("/monitoring/groupmetrictypes", new GroupMetricTypesHandler());
        HANDLERS.put("/monitoring/groupmetricnames", new GroupMetricNamesHandler());
        HANDLERS.put("/monitoring/grouphealthstatus", new GroupHealthStatusHandler());
        HANDLERS.put("/monitoring/grouplasthealthstatus", new GroupLatestValidHealthStatusHandler());
        //new MonitoringHttpListener().run(port);
    }
    
    //public static void main(String... args) throws IOException {
    //    init();
    //}
}
