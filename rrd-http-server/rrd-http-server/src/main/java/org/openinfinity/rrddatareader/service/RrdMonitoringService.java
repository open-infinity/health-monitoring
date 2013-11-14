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

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.codehaus.jackson.Version;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.SerializationConfig.Feature;
import org.codehaus.jackson.map.module.SimpleModule;
import org.openinfinity.healthmonitoring.http.response.AbstractResponse;
import org.openinfinity.healthmonitoring.http.response.GroupListResponse;
import org.openinfinity.healthmonitoring.http.response.HealthStatusResponse;
import org.openinfinity.healthmonitoring.http.response.HealthStatusResponse.SingleHealthStatus;
import org.openinfinity.healthmonitoring.http.response.MetricBoundariesResponse;
import org.openinfinity.healthmonitoring.http.response.MetricNamesResponse;
import org.openinfinity.healthmonitoring.http.response.MetricTypesResponse;
import org.openinfinity.healthmonitoring.http.response.NodeListResponse;
import org.openinfinity.healthmonitoring.http.response.NotificationResponse;
import org.openinfinity.healthmonitoring.model.Node;
import org.openinfinity.healthmonitoring.model.Notification;
import org.openinfinity.healthmonitoring.model.RrdValue;
import org.openinfinity.rrddatareader.InvalidResourceException;
import org.openinfinity.rrddatareader.util.CustomDoubleSerializer;
import org.openinfinity.rrddatareader.util.FileUtil;
import org.openinfinity.rrddatareader.util.GroupMetricFileParser;
import org.openinfinity.rrddatareader.util.NotificationFileParser;
import org.openinfinity.rrddatareader.util.PropertiesReader;
import org.openinfinity.rrddatareader.util.RrdDataParser;
import org.openinfinity.rrddatareader.util.ThresholdFileParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.sourceforge.jrrd.ConsolidationFunctionType;


public class RrdMonitoringService implements MonitoringService {

    private static final Logger LOGGER = LoggerFactory.getLogger(RrdMonitoringService.class);

    public static final String METRIC_NAME_DELIMITER = "[+]";
    
    public static int NUMBER_OF_COLUMNS_IN_CONF_FILE = 6;
    
    private final int PERIOD = 20000;


    @Override
    public String getHealthStatus(String hostName, String dataType, String metricNames, Date startTime, Date endTime,
            Long step) {
        HealthStatusResponse response = new HealthStatusResponse();
        for (String metricName : metricNames.split(METRIC_NAME_DELIMITER)) {
            SingleHealthStatus status = new SingleHealthStatus();
            String fileName =
                    composeRrdDBFileName(PropertiesReader.getString("rrdDirectoryPath"), hostName, dataType,
                            metricName);
            Map<String, List<RrdValue>> rrdData = 
                RrdDataParser.parseRrdFile(fileName, startTime, endTime, step, ConsolidationFunctionType.AVERAGE);
            if (rrdData != null) {
                status.setResponseStatus(AbstractResponse.STATUS_OK);
                status.setValues(rrdData);
                status.setName(metricName);
            } else {
                // TODO revise later
                if (isNodeActive(hostName)) {
                    // if metric is unavailable but node is available
                    status.setResponseStatus(AbstractResponse.STATUS_METRIC_FAIL);
                } else {
                    status.setResponseStatus(AbstractResponse.STATUS_NODE_FAIL);
                }
            }
            response.getMetrics().add(status);
        }

        return toJson(response);
    }

    public boolean isNodeActive(String hostName) {
        List<Node> activeNodes = getNodeListResponse().getActiveNodes();
        for (Node node : activeNodes) {
            if (node.getNodeName().equalsIgnoreCase(hostName)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public String getNodeList() {
        NodeListResponse response = getNodeListResponse();
        return toJson(response);
    }

    protected NodeListResponse getNodeListResponse() {
        NodeListResponse response = new NodeListResponse();
        try {
            List<String> nodeDescriptions = FileUtil.readFile(PropertiesReader.getString("nodesListPath"));
            List<Node> nodes = createNodeList(nodeDescriptions, false);
            List<String> activeNodeDescriptions = FileUtil.readFile(PropertiesReader.getString("activeNodesListPath"));
            List<Node> activeNodes = createNodeList(activeNodeDescriptions, false);
      
            Comparator<Node> comparator = new Comparator<Node>() {
                @Override
                public int compare(Node n1, Node n2) {
                    return n1.getNodeName().compareTo(n2.getNodeName());
                }
            };
            
            // FIXME: use Collection.removeAll()
            Collections.sort(activeNodes, comparator);
            List<Node> inactiveNodes =  new ArrayList<Node>();

            for (Node n : nodes) {
                int index = Collections.binarySearch(activeNodes, n, comparator);
                if (index < 0) {               
                    inactiveNodes.add(n);
                }
            }
            response.setActiveNodes(activeNodes);
            response.setInactiveNodes(inactiveNodes);
            response.setResponseStatus(AbstractResponse.STATUS_OK);
        } 
     
        catch (UnsupportedOperationException e){
            LOGGER.error("UnsupportedOperationException: ", e);
            response.setResponseStatus(AbstractResponse.STATUS_RRD_FAIL);
        } 
        catch(ClassCastException e){
            LOGGER.error("ClassCastException: ", e);
            response.setResponseStatus(AbstractResponse.STATUS_RRD_FAIL);
        } 
        catch(NullPointerException e) {
            LOGGER.error("NullPointerException: ", e);
            response.setResponseStatus(AbstractResponse.STATUS_RRD_FAIL);
        }
        
        return response;
    }

    @Override
    public String getMetricTypes(String nodeName) {
        MetricTypesResponse response = getMetricTypesResponse(nodeName);
        return toJson(response);
    }

    protected MetricTypesResponse getMetricTypesResponse(String nodeName) {
        MetricTypesResponse response = new MetricTypesResponse();
        if (nodeName != null) {
            try {
                List<String> metricTypes = getFileNames(nodeName, null, null, true);
                response.setResponseStatus(AbstractResponse.STATUS_OK);
                response.setMetricTypes(metricTypes);
            } catch (InvalidResourceException e) {
                LOGGER.error("InvalidResourceException: ", e);
                response.setResponseStatus(AbstractResponse.STATUS_RRD_FAIL);
            }
        } else {
            response.setResponseStatus(AbstractResponse.STATUS_PARAM_FAIL);
        }
        return response;
    }

    @Override
    public String getGroupMetricTypes(String groupName) {
        MetricTypesResponse response = new MetricTypesResponse();
        if (groupName != null) {

            Set<String> nodeNames = getGroupListResponse().getGroups().get(groupName);

            List<String> list = null;

            for (String nodeName : nodeNames) {
                MetricTypesResponse metricTypesResponse = getMetricTypesResponse(nodeName);
                List<String> metricTypes = metricTypesResponse.getMetricTypes();
                if (list == null) {
                    list = new ArrayList<String>(metricTypes);
                } else {
                    list.retainAll(metricTypes);
                }
            }
            response.setMetricTypes(list);
            response.setResponseStatus(AbstractResponse.STATUS_OK);
        } else {
            response.setResponseStatus(AbstractResponse.STATUS_PARAM_FAIL);
        }
        return toJson(response);
    }

    @Override
    public String getMetricNames(String nodeName, String metricType) {
        MetricNamesResponse response = new MetricNamesResponse();
        if (nodeName != null && metricType != null) {
            try {
                List<String> metricNames = getFileNames(nodeName, metricType, null, false);
                response.setResponseStatus(AbstractResponse.STATUS_OK);
                response.setMetricNames(metricNames);
            } catch (InvalidResourceException e) {
                LOGGER.error("InvalidResourceException: ", e);
                response.setResponseStatus(AbstractResponse.STATUS_RRD_FAIL);
            }
        } else {
            response.setResponseStatus(AbstractResponse.STATUS_PARAM_FAIL);
        }
        return toJson(response);
    }

    @Override
    public String getGroupMetricNames(String groupName, String metricType) {
        List<Node> members = findGroupMembers(groupName, false);
        if (members.size() > 0) {
            return getMetricNames(members.get(0).getNodeName(), metricType);
        } else {
            return getMetricNames(null, metricType);
        }
    }

    public String getGroupList2() {
        GroupListResponse groupListResponse = new GroupListResponse();
        List<String> groupNames = new GroupMetricFileParser().getGroupNames();
        for (String groupName : groupNames) {
            if (groupListResponse.getGroups().get(groupName) == null) {
                groupListResponse.getGroups().put(groupName, new HashSet<String>());
            }
            List<Node> nodes = findGroupMembers(groupName, false);
            for (Node node : nodes) {
                groupListResponse.getGroups().get(node.getGroupName()).add(node.getNodeName());
            }
        }
        groupListResponse.setResponseStatus(AbstractResponse.STATUS_OK);
        return toJson(groupListResponse);
    }

    @Override
    public String getGroupList() {
        GroupListResponse groupListResponse = getGroupListResponse();
        return toJson(groupListResponse);
    }
    
    protected GroupListResponse getGroupListResponse() {
        GroupListResponse groupListResponse = new GroupListResponse();
        NodeListResponse nodeListResponse = getNodeListResponse();

        for (Node node : nodeListResponse.getActiveNodes()) {
            if (groupListResponse.getGroups().get(node.getGroupName()) == null) {
                groupListResponse.getGroups().put(node.getGroupName(), new HashSet<String>());
            }
            groupListResponse.getGroups().get(node.getGroupName()).add(node.getNodeName());
        }

        groupListResponse.setResponseStatus(AbstractResponse.STATUS_OK);
        return groupListResponse;
    }

    @Override
    public String getGroupHealthStatus(String groupName, String metricType, String metricNames, Date startTime,
            Date endTime, Long step) {
        HealthStatusResponse response = new HealthStatusResponse();

        for (String metricName : metricNames.split(METRIC_NAME_DELIMITER)) {
            SingleHealthStatus status = new SingleHealthStatus();
            List<Node> members = findGroupMembers(groupName, false);
            Set<Map<String, List<RrdValue>>> nodesStats = new HashSet<Map<String, List<RrdValue>>>();
            Map<String, List<RrdValue>> total = new HashMap<String, List<RrdValue>>() {

                /**
                 * serialVersionUID
                 */
                private static final long serialVersionUID = 574781496514309416L;

                @Override
                public List<RrdValue> put(String key, List<RrdValue> value) {
                    List<RrdValue> list = get(key);
                    if (list == null) {
                        return super.put(key, value);
                    }
                    for (RrdValue toAdd : value) {
                        boolean exists = false;
                        for (RrdValue rrdV : list) {
                            if (rrdV.getDate() == toAdd.getDate()) {
                                // FIXME: this does not calculate average.
                                // Actually it is unclear what was intention here.
                                // Rewrite of logic needed.
                                double newValue = (rrdV.getValue() + toAdd.getValue()) / 2;
                                rrdV.setValue(newValue);
                                exists = true;
                                break;
                            }
                        }
                        if (!exists) {
                            list.add(toAdd);
                        }
                    }
                    return list;
                }
            };
            for (Node node : members) {
                String fileName =
                        composeRrdDBFileName(PropertiesReader.getString("rrdDirectoryPath"), node.getNodeName(),
                                metricType, metricName);
                Map<String, List<RrdValue>> rrdData = 
                    RrdDataParser.parseRrdFile(fileName, startTime, endTime, step, ConsolidationFunctionType.AVERAGE);
                
                // FIXME: handle properly errors in rrd parsing
                // Added null pointer check
                if (rrdData != null){
                    for (String metricSubName : rrdData.keySet()) {
                        List<RrdValue> values = rrdData.get(metricSubName);
                        total.put(metricSubName, values);
                    }
                }
            }

            status.setResponseStatus(AbstractResponse.STATUS_OK);
            status.setValues(total);
            status.setName(metricName);

            response.getMetrics().add(status);
        }
        return toJson(response);
    }
    
  
        
    /* This function fetches the latest available group status for give metric type.
     * More details:Group status is calculate as average.
     * For each node, the latest available metric is used for group average calculation.
     */
    @Override
    public String getLatestValidGroupHealthStatus(String groupName, String metricType, 
        String metricNames, Date endTime, Long step) {
        
        HealthStatusResponse response = new HealthStatusResponse();
        Date startTime = new Date(endTime.getTime() - PERIOD);
        
        for (String metricName : metricNames.split(METRIC_NAME_DELIMITER)) {
            SingleHealthStatus status = new SingleHealthStatus();
            List<Node> members = findGroupMembers(groupName, true);
            Set<Map<String, List<RrdValue>>> nodesStatsMap = new HashSet<Map<String, List<RrdValue>>>();

            
            // Combined metrics (average)
            // Map.put function is overriden so that Rrd values list being added 
            // is sorted, so that the newest non-NaN item is first in the list
            Map<String, List<RrdValue>> groupAverageMap = new HashMap<String, List<RrdValue>>() {

                /**
                 * serialVersionUID
                 */
                private static final long serialVersionUID = 574781496514309416L;

                @Override
                public List<RrdValue> put(String key, List<RrdValue> rrdValuesList) {
                    Collections.sort(rrdValuesList, new Comparator<RrdValue>() {
                        @Override
                        public int compare(RrdValue o1, RrdValue o2) {
                           
                           if (LOGGER.isTraceEnabled()){
                               LOGGER.trace("o1:{}", String.valueOf( (double)o1.getValue() ));
                               LOGGER.trace("o2:{}", String.valueOf( (double)o2.getValue() ));
                           }

                            if (Double.isNaN(o2.getValue())){
                                LOGGER.trace("Sorting NaN");
                                return -1;
                            }
                            if(o1.getDate() > o2.getDate() ){
                                return -1;
                               }
                               else if(o1.getDate() < o2.getDate()){
                                   return 1;
                               }
                               return 0;
                        }
                    });

                    List<RrdValue> totalsList = get(key);         
                    if (totalsList == null) {
                        return super.put(key, rrdValuesList);
                    }
                    
                    // Log list before adding next node data
                    if (LOGGER.isTraceEnabled()){
                        for (RrdValue rrdV : totalsList){
                            LOGGER.trace("totalsList item: value:{}", rrdV.getValue());
                            LOGGER.trace("totalsList item: date:{}", String.valueOf( rrdV.getDate() ));
                        }
                    }
                    // Find the newest value in the list
                    RrdValue nodeSingleValue = null;
                    for (RrdValue rrdV : rrdValuesList){
                        if (LOGGER.isTraceEnabled()){
                            LOGGER.trace("Value single:{}", String.valueOf( (double)rrdV.getValue() ));
                        }
                        if (!Double.isNaN(rrdV.getValue())){
                            LOGGER.trace("Found value");
                            nodeSingleValue = rrdV;
                            break;
                        }
                        LOGGER.trace("Found NaN");
                    }
                    
                    // Use the newest metric - position 0 in the list
                    RrdValue totalValue = totalsList.get(0);
                    long svDate = nodeSingleValue.getDate();
                    
                    // Set time stamp to oldest value
                    if (svDate < totalValue.getDate()){
                        totalValue.setDate(svDate);
                    }
                    totalValue.setValue(totalValue.getValue() + nodeSingleValue.getValue());

                    // Log lists 
                    if (LOGGER.isTraceEnabled()){
                        for (RrdValue rrdV : rrdValuesList){ 
                            LOGGER.trace("rrdValuesList item: value:{}", String.valueOf( (double)rrdV.getValue() ));
                            LOGGER.trace("rrdValuesList item: date:{}", String.valueOf(rrdV.getDate() ));
                        }
     
                        for (RrdValue rrdV : totalsList){
                            LOGGER.trace("totalsList item: value:{}", rrdV.getValue());
                            LOGGER.trace("totalsList item: date:{}", String.valueOf( rrdV.getDate() ));
                        }
                    }
                    
                    return totalsList;
                }
            };
            boolean metricsAvailable = false;
            for (Node node : members) {
                String fileName = composeRrdDBFileName(
                    PropertiesReader.getString("rrdDirectoryPath"), node.getNodeName(), metricType, metricName);
                LOGGER.trace("parseRrdFile time", endTime);
                
                // Single node metrics
                Map<String, List<RrdValue>> rrdData = 
                    RrdDataParser.parseRrdFile(fileName, startTime, endTime, step, ConsolidationFunctionType.AVERAGE);
                
                if (rrdData != null){
                    for (String metricSubName : rrdData.keySet()) {
                        LOGGER.trace("metric subname:{}", metricSubName);
                        List<RrdValue> values = rrdData.get(metricSubName);
                        LOGGER.trace("List<RrdValue> values: {}", values.size());
                        groupAverageMap.put(metricSubName, values);
                    }
                    metricsAvailable = true;         
                }
            }                    
            if (!metricsAvailable){
                LOGGER.trace("Metrics not available");
                status.setResponseStatus(AbstractResponse.STATUS_METRIC_FAIL);
            }
            else{
                status.setResponseStatus(AbstractResponse.STATUS_OK);
                status.setValues(calculateAverageStats(groupAverageMap, members.size()));
                status.setName(metricName);
            }
            response.getMetrics().add(status);
        }
        return toJson(response);
    }
    
    private Map<String, List<RrdValue>> calculateAverageStats(Map<String, List<RrdValue>> total, int clusterSize) {
        if (clusterSize < 1) {
            return null;
        }
        Map<String, List<RrdValue>> avg = new HashMap<String, List<RrdValue>>();
        
        for (String key : total.keySet()) {
            LOGGER.trace("key:{}", key);
            List<RrdValue> rrdValueList = total.get(key);
            RrdValue rrdValue = rrdValueList.get(0);
            LOGGER.trace("rrdValue: {}", rrdValue);
            double value = rrdValue.getValue();
            rrdValue.setValue(value / clusterSize); 
            LOGGER.trace("value/clusterSize:{}", rrdValue.getValue());
            
            List<RrdValue> avgValueList = new ArrayList<RrdValue>();
            avgValueList.add(rrdValue);
            avg.put(key, avgValueList);
        }
        return avg;
    }
        
    @Override                    

    public String getNotifications(Long startTime, Long endTime) {
        List<Notification> notifications = NotificationFileParser.getNotifications(startTime, endTime);

        Collections.sort(notifications, new Comparator<Notification>() {

            @Override
            public int compare(Notification o1, Notification o2) {
                if (o1 != null) {
                    if (o2 != null) {
                        if (o1.getTime() != null && o2.getTime() != null) {
                            return o1.getTime().compareTo(o2.getTime());
                        }
                    } else {
                        return -1;
                    }
                } else if (o2 != null) {
                    if (o2.getTime() != null) {
                        return 1;
                    }
                }
                return 0;
            }
        });

        NotificationResponse response = new NotificationResponse();
        response.setNotifications(notifications);
        response.setResponseStatus(AbstractResponse.STATUS_OK);
        return toJson(response);
    }

    @Override
    public String getBoundaries(String metricType) {
        Map<String, Map<String, Map<String, String>>> boundaries =
                new ThresholdFileParser().getBoundaries(metricType);
        MetricBoundariesResponse response = new MetricBoundariesResponse();
        response.setBoundaries(boundaries);
        response.setResponseStatus(AbstractResponse.STATUS_OK);
        return toJson(response);
    }

    /* (non-Javadoc)
     * @see org.openinfinity.rrddatareader.service.MonitoringService#getNotSentNotifications()
     */
    @Override
    public List<Notification> getNotSentNotifications() {
        return NotificationFileParser.getNotSentNotifications();
    }

    /* (non-Javadoc)
     * @see org.openinfinity.rrddatareader.service.MonitoringService#markNotificationAsSent(java.util.List)
     */
    @Override
    public void markNotificationAsSent(List<Notification> notifications) {
        NotificationFileParser.markNotificationAsSent(notifications);
    }



    private List<String> getFileNames(String nodeName, String dataType, String metricName, boolean onlyDirs)
            throws InvalidResourceException {
        return RrdDataParser.getStructure(
                composeRrdDBFileName(PropertiesReader.getString("rrdDirectoryPath"), nodeName, dataType, null),
                onlyDirs);
    }

    private <T extends Serializable> String toJson(T serializable) {
        String result = new String();
        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule("simpleModule", new Version(1, 0, 0, null));
        module.addSerializer(new CustomDoubleSerializer());
        mapper.registerModule(module);
        mapper.getSerializationConfig().without(Feature.USE_ANNOTATIONS);
        try {
            result = mapper.writeValueAsString(serializable);
        } catch (JsonMappingException e) {
            LOGGER.error("JsonMappingException: ", e);
        } catch (IOException e) {
            LOGGER.error("IOException:", e);
        }
        return result;
    }

    private String composeRrdDBFileName(String baseDir, String hostName, String dataType, String metricName) {
        StringBuilder builder = new StringBuilder(baseDir).append(File.separator);
        if (hostName != null) {
            builder.append(hostName).append(File.separator);
        }
        if (dataType != null) {
            builder.append(dataType).append(File.separator);
        }
        if (metricName != null) {
            builder.append(metricName);
        }
        return builder.toString();
    }

    private List<Node> createNodeList(List<String> hostLines, boolean excludeLoadBalancer) {
        List<Node> nodes = new ArrayList<Node>();
        for (String line : hostLines) {
            if (line != null && !"".equals(line.trim())) {
                String[] parts = line.split("\\s+");
                if (parts.length == NUMBER_OF_COLUMNS_IN_CONF_FILE) {
                    Node node = new Node();
                    node.setIpAddress(parts[1]);
                    node.setNodeName(parts[2]);
                    node.setGroupName(parts[5]);   
                    if (excludeLoadBalancer && ("loadbalancer").equals(parts[3])){
                        continue;
                    }
                    nodes.add(node);
                }
            }
        }
        return nodes;
    }

    private List<Node> findGroupMembers(String groupName, boolean excludeLoadBalancer) {
        List<Node> members = new ArrayList<Node>();
        if (groupName != null && !"".equals(groupName.trim())) {
            List<Node> nodeList = createNodeList(FileUtil.readFile(
                PropertiesReader.getString("activeNodesListPath")), excludeLoadBalancer);
            for (Node node : nodeList) {
                if (groupName.equals(node.getGroupName())) {
                    members.add(node);
                }
            }
        }
        return members;
    }

}
