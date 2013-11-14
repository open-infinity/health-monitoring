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

import java.util.Date;
import java.util.List;

import org.openinfinity.healthmonitoring.model.Notification;

public interface MonitoringService {

    String getHealthStatus(String hostName, String dataType, String metricNames, Date startTime, Date endTime,
            Long step);

    String getNodeList();

    String getMetricTypes(String hostName);

    String getMetricNames(String hostName, String dataType);

    String getGroupList();

    String getGroupMetricNames(String groupName, String metricType);

    String getGroupMetricTypes(String groupName);

    String getGroupHealthStatus(String groupName, String metricType, String metricNames, Date startTime,
            Date endTime, Long step);
    
    String getLatestValidGroupHealthStatus(String groupName, String metricType, String metricNames, Date time, Long step);

    String getNotifications(Long startTime, Long endTime);

    List<Notification> getNotSentNotifications();

    String getBoundaries(String metricType);

    void markNotificationAsSent(List<Notification> notifications);
}
