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

import org.jboss.netty.buffer.ChannelBuffers;
import org.jboss.netty.handler.codec.http.HttpResponse;
import org.jboss.netty.handler.codec.http.QueryStringDecoder;
import org.openinfinity.rrddatareader.service.MonitoringService;
import org.openinfinity.rrddatareader.service.RrdMonitoringService;
import org.openinfinity.rrddatareader.util.HttpUtil;

import java.util.Date;

class HealthStatusHandler implements AbstractHandler {

    @Override
    public void handle(HttpResponse response, QueryStringDecoder queryStringDecoder) throws Exception {
        String hostName = HttpUtil.get(queryStringDecoder, "hostName");

        String startTime = HttpUtil.get(queryStringDecoder, "startTime");
        String endTime = HttpUtil.get(queryStringDecoder, "endTime");
        String step = HttpUtil.get(queryStringDecoder, "step");
        String dataType = HttpUtil.get(queryStringDecoder, "metricType");
        String metricNames = HttpUtil.get(queryStringDecoder, "metricNames");

        MonitoringService monitoringService = new RrdMonitoringService();
        response.setContent(ChannelBuffers.copiedBuffer(monitoringService.getHealthStatus(hostName, dataType,
                metricNames, new Date(Long.valueOf(startTime)), new Date(Long.valueOf(endTime)),
                Long.valueOf(step)).getBytes()));
    }
}
