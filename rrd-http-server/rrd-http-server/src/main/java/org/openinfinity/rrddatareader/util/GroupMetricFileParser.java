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
package org.openinfinity.rrddatareader.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.StringTokenizer;

public class GroupMetricFileParser {

    private static final Logger LOGGER = LoggerFactory.getLogger(ThresholdFileParser.class);
    private static Map<String, Map<String, List<String>>> cache;

    public List<String> getGroupNames() {
        read();
        Set<String> keySet = cache.keySet();
        return new ArrayList<String>(keySet);
    }

    public List<String> getGroupMetricTypes(String groupName) {
        read();
        Set<String> set = cache.get(groupName) != null ? cache.get(groupName).keySet() : null;
        return set != null ? new ArrayList<String>(set) : null;
    }

    public List<String> getGroupMetricNames(String groupName, String metricType) {
        read();
        Map<String, List<String>> types = cache.get(groupName) != null ? cache.get(groupName) : null;
        if (types != null) {
            return types.get(metricType);
        }
        return null;
    }

    private void read() {
        synchronized (this) {
            if (cache == null) {
                LOGGER.debug("Cache is empty. Parsing file");
                String filePath = PropertiesReader.getString("groupMetricConfPath");
                cache = parse(filePath);
            }
        }
    }

    private Map<String, Map<String, List<String>>> parse(String file) {
        LOGGER.debug("Parsing file " + file);
        Map<String, Map<String, List<String>>> result = new HashMap<String, Map<String, List<String>>>();

        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(file));
            for (String line = reader.readLine(); line != null; line = reader.readLine()) {
                if (!line.isEmpty() && !"#".equals(line.substring(0, 1))) {
                    StringTokenizer tokenizer = new StringTokenizer(line, "#");
                    if (tokenizer.countTokens() == 3) {
                        String groupName = tokenizer.nextToken();
                        String metricType = tokenizer.nextToken();
                        String metricName = tokenizer.nextToken();
                        if (!groupName.isEmpty() && !metricType.isEmpty() && !metricName.isEmpty()) {
                            addElement(result, groupName, metricType, metricName);
                        }
                    }
                } else {
                    LOGGER.warn("Line is incorrect: '{}'", line);
                }
            }
        } catch (IOException e) {
            LOGGER.error("IOException while parsing file '" + file + "'", e);
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    LOGGER.error("IOException while closing reader for file '" + file + "'", e);
                }
            }
        }
        return result;
    }

    private void addElement(Map<String, Map<String, List<String>>> result, String groupName, String metricType,
                            String metricName) {
        Map<String, List<String>> types = result.get(groupName);
        if (types == null) {
            types = new HashMap<String, List<String>>();
            types.put(metricType, null);
        }
        result.put(groupName, types);
        List<String> names = types.get(metricType);
        if (names == null) {
            names = new ArrayList<String>();
        }
        names.add(metricName);
        types.put(metricType, names);
    }
}
