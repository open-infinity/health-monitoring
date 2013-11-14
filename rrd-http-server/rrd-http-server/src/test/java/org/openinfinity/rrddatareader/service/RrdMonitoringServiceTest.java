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
package org.openinfinity.rrddatareader.service;

import junit.framework.TestCase;
import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.openinfinity.healthmonitoring.http.response.AbstractResponse;
import org.openinfinity.healthmonitoring.http.response.GroupListResponse;
import org.openinfinity.healthmonitoring.http.response.HealthStatusResponse;
import org.openinfinity.healthmonitoring.http.response.HealthStatusResponse.SingleHealthStatus;
import org.openinfinity.healthmonitoring.http.response.MetricNamesResponse;
import org.openinfinity.healthmonitoring.http.response.MetricTypesResponse;
import org.openinfinity.healthmonitoring.http.response.NodeListResponse;
import org.openinfinity.healthmonitoring.model.Node;
import org.openinfinity.healthmonitoring.model.RrdValue;

import java.io.IOException;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

public class RrdMonitoringServiceTest {

    private MonitoringService monitoringService;

    private ObjectMapper mapper;

    @Before
    public void setUp() {
        monitoringService = new RrdMonitoringService();
        mapper = new ObjectMapper();
    }

    @Test
    public void testGetNodeList() throws JsonParseException, JsonMappingException, IOException {
        NodeListResponse nodeListResponse = mapper.readValue(monitoringService.getNodeList(), NodeListResponse.class);

        TestCase.assertEquals(0, nodeListResponse.getResponseStatus());
        TestCase.assertEquals(2, nodeListResponse.getActiveNodes().size());
        TestCase.assertEquals(1, nodeListResponse.getInactiveNodes().size());
        
        Node inactiveNode = new Node();
        inactiveNode.setGroupName("main");
        inactiveNode.setIpAddress("10.33.2.12");
        inactiveNode.setNodeName("c3.com");

        TestCase.assertTrue(nodeListResponse.getInactiveNodes().contains(inactiveNode));
    }

    @Test
    public void testGetMetricTypes() throws JsonParseException, JsonMappingException, IOException {
        MetricTypesResponse actual1 = mapper.readValue(monitoringService.getMetricTypes("c1.com"), MetricTypesResponse.class);
        TestCase.assertEquals(0, actual1.getResponseStatus());
        TestCase.assertEquals(2, actual1.getMetricTypes().size());
        TestCase.assertTrue(actual1.getMetricTypes().contains("memory"));
        TestCase.assertTrue(actual1.getMetricTypes().contains("load"));

        MetricTypesResponse actual2 = mapper.readValue(monitoringService.getMetricTypes("c4.com"), MetricTypesResponse.class);
        TestCase.assertEquals(0, actual2.getResponseStatus());
        TestCase.assertEquals(0, actual2.getMetricTypes().size());

        MetricTypesResponse actual3 = mapper.readValue(monitoringService.getMetricTypes(null), MetricTypesResponse.class);
        TestCase.assertEquals(AbstractResponse.STATUS_PARAM_FAIL, actual3.getResponseStatus());
        TestCase.assertEquals(null, actual3.getMetricTypes());
    }

    @Test
    public void testGetMetricNames() throws JsonParseException, JsonMappingException, IOException {
        MetricNamesResponse actual1 = mapper.readValue(monitoringService.getMetricNames("c1.com", "load"), MetricNamesResponse.class);
        TestCase.assertEquals(0, actual1.getResponseStatus());
        TestCase.assertEquals("load.rrd", actual1.getMetricNames().get(0));
        TestCase.assertEquals(1, actual1.getMetricNames().size());

        MetricNamesResponse actual2 = mapper.readValue(monitoringService.getMetricNames("c1.com", null), MetricNamesResponse.class);
        TestCase.assertEquals(AbstractResponse.STATUS_PARAM_FAIL, actual2.getResponseStatus());
        TestCase.assertEquals(null, actual2.getMetricNames());

        MetricNamesResponse actual3 = mapper.readValue(monitoringService.getMetricNames(null, null), MetricNamesResponse.class);
        TestCase.assertEquals(AbstractResponse.STATUS_PARAM_FAIL, actual3.getResponseStatus());
        TestCase.assertEquals(null, actual3.getMetricNames());

        MetricNamesResponse actual4 = mapper.readValue(monitoringService.getMetricNames("xxxxxx", "yyyyy"), MetricNamesResponse.class);
        TestCase.assertEquals(1, actual4.getResponseStatus());
        TestCase.assertEquals(null, actual4.getMetricNames());
    }

    @Test
    @Ignore
    public void testGetHealthStatus() throws JsonParseException, JsonMappingException, IOException {
        Calendar calendar = Calendar.getInstance();
        calendar.set(Calendar.YEAR, 2012);
        calendar.set(Calendar.MONTH, Calendar.JANUARY);
        calendar.set(Calendar.DATE, 18);
        calendar.set(Calendar.HOUR_OF_DAY, 9);
        calendar.set(Calendar.MINUTE, 0);
        calendar.set(Calendar.SECOND, 0);
        Date startTime = calendar.getTime();
        Date endTime = calendar.getTime();

        HealthStatusResponse actual = mapper.readValue(monitoringService.getHealthStatus("c1.com", "load", "load.rrd", startTime, endTime, 1000L), HealthStatusResponse.class);
        SingleHealthStatus singleActual = actual.getMetrics().get(0);

        TestCase.assertEquals("load.rrd", singleActual.getName());
        TestCase.assertEquals(0, singleActual.getResponseStatus());
        TestCase.assertEquals(3, singleActual.getValues().size());
        TestCase.assertTrue(singleActual.getValues().containsKey("midterm"));
        TestCase.assertTrue(singleActual.getValues().containsKey("shortterm"));
        TestCase.assertTrue(singleActual.getValues().containsKey("longterm"));
        TestCase.assertTrue(singleActual.getValues().get("midterm").contains(new RrdValue(new Date(1326866500000L), 0D)));
        TestCase.assertTrue(singleActual.getValues().get("shortterm").contains(new RrdValue(new Date(1326866500000L), 0D)));
    }

    @Test
    @Ignore
    public void testGetGroupList() throws JsonParseException, JsonMappingException, IOException {
        GroupListResponse actual = mapper.readValue(monitoringService.getGroupList(), GroupListResponse.class);

        TestCase.assertEquals(0, actual.getResponseStatus());
        TestCase.assertEquals(1, actual.getGroups().size());
        TestCase.assertNotNull(actual.getGroups().get("server"));
        TestCase.assertNull(actual.getGroups().get("bi"));
    }

    @Test
    @Ignore
    public void testGetGroupHealthStatus() throws JsonParseException, JsonMappingException, IOException {
        HealthStatusResponse c1HealthStatus = mapper.readValue(monitoringService.getHealthStatus("c1.com", "memory", "memory-free.rrd", new Date(1326979550000L), new Date(1326979550000L), 1000L), HealthStatusResponse.class);
        SingleHealthStatus singleC1HealthStatus = c1HealthStatus.getMetrics().get(0);
        HealthStatusResponse c3HealthStatus = mapper.readValue(monitoringService.getHealthStatus("c3.com", "memory", "memory-free.rrd", new Date(1326979550000L), new Date(1326979550000L), 1000L), HealthStatusResponse.class);
        SingleHealthStatus singleC3HealthStatus = c3HealthStatus.getMetrics().get(0);
        HealthStatusResponse groupHealthStatus = mapper.readValue(monitoringService.getGroupHealthStatus("main", "memory", "memory-free.rrd", new Date(1326979550000L), new Date(1326979550000L), 1000L), HealthStatusResponse.class);
        SingleHealthStatus singleGroupHealthStatus = groupHealthStatus.getMetrics().get(0);
        TestCase.assertEquals(1, singleGroupHealthStatus.getValues().size());

        List<RrdValue> groupValues = singleGroupHealthStatus.getValues().get(singleGroupHealthStatus.getValues().keySet().iterator().next());
        TestCase.assertEquals(2, groupValues.size());

        RrdValue c1Latest = singleC1HealthStatus.getValues().get("value").get(0);
        RrdValue c3Latest = singleC3HealthStatus.getValues().get("value").get(0);
        RrdValue groupLatest = singleGroupHealthStatus.getValues().get("value").get(0);
        for (int i = 1; i < singleC1HealthStatus.getValues().get("value").size(); i++) {
            if (singleC1HealthStatus.getValues().get("value").get(i).getDate() > c1Latest.getDate()) {
                c1Latest = singleC1HealthStatus.getValues().get("value").get(i);
            }
            if (singleC3HealthStatus.getValues().get("value").get(i).getDate() > c3Latest.getDate()) {
                c3Latest = singleC3HealthStatus.getValues().get("value").get(i);
            }
            if (singleGroupHealthStatus.getValues().get("value").get(i).getDate() > groupLatest.getDate()) {
                groupLatest = singleGroupHealthStatus.getValues().get("value").get(i);
            }
        }
        TestCase.assertEquals((c1Latest.getValue() + c3Latest.getValue()) / 2, groupLatest.getValue());
    }
}
