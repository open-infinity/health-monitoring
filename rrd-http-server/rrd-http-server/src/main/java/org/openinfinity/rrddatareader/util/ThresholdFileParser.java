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
import java.util.HashMap;
import java.util.Map;
import java.util.StringTokenizer;

public class ThresholdFileParser {

    private static final Logger LOGGER = LoggerFactory.getLogger(ThresholdFileParser.class);

    private static Map<String, Map<String, Map<String, Map<String, String>>>> cache;

    public Map<String, Map<String, Map<String, String>>> getBoundaries(String metricType) {
        synchronized (this) {
            if (cache == null) {
                LOGGER.debug("Cache is empty. Parsing file");
                String filePath = PropertiesReader.getString("metricBoundariesFilePath");
                cache = parse(filePath);
                LOGGER.info("Cache: " + cache);
            }
        }
        Map<String, Map<String, Map<String, String>>> map = cache.get(metricType);
        return map;
    }


    private Map<String, Map<String, Map<String, Map<String, String>>>> parse(String file) {
        LOGGER.debug("Parsing file " + file);
        Map<String, Map<String, Map<String, Map<String, String>>>> result =
                new HashMap<String, Map<String, Map<String, Map<String, String>>>>();

        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(file));
            for (String line = reader.readLine(); line != null; line = reader.readLine()) {
                String plugin = null;
                String pluginInstance = null;
                String typeInstance = null;
                String type = null;
                String datasource = null;
                String name = null;
                String value = null;
                if (!line.isEmpty() && !"#".equals(line.substring(0, 1))) {
                    StringTokenizer tokenizer = new StringTokenizer(line, "#");
                    if (tokenizer.countTokens() == 2) {
                        String fullName = tokenizer.nextToken();
                        String threshold = tokenizer.nextToken();

                        String[] fullNameTokenizer = fullName.split("\\.");
                        String[] thresholdTokenizer = threshold.split("=");
                        if (fullNameTokenizer.length >= 4) {
                            plugin = fullNameTokenizer[0];
                            pluginInstance = fullNameTokenizer[1];
                            type = fullNameTokenizer[2];
                            typeInstance = fullNameTokenizer[3];
                            datasource = null;
                            if (fullNameTokenizer.length > 4) {
                                datasource = fullNameTokenizer[4];
                            } else {
                                datasource = "values";
                            }
                        }
                        if (thresholdTokenizer.length == 2) {
                            name = thresholdTokenizer[0];
                            value = thresholdTokenizer[1];
                        }
                    }
                    if (plugin == null || type == null || name == null || value == null) {
                        LOGGER.warn("Seems that line is incorrect: '" + line + "'");
                        break;
                    }
                    addElement(result, plugin, pluginInstance, type, typeInstance, datasource, name, value);
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

    private void addElement(Map<String, Map<String, Map<String, Map<String, String>>>> result, String plugin,
                            String pluginInstance, String type, String typeInstance, String datasource, String name,
                            String value) {
        String metricTypeLabel = pluginInstance != null && !"".equals(pluginInstance.trim()) ? plugin + "-"
                + pluginInstance : plugin;
        String metricNameLabel = typeInstance != null && !"".equals(typeInstance.trim()) ? type + "-"
                + typeInstance : type;

        Map<String, Map<String, Map<String, String>>> metricTypesMap = result.get(metricTypeLabel);
        if (metricTypesMap == null) {
            metricTypesMap = new HashMap<String, Map<String, Map<String, String>>>();
            result.put(metricTypeLabel, metricTypesMap);
        }
        Map<String, Map<String, String>> metricnamesMap = metricTypesMap.get(metricNameLabel);
        if (metricnamesMap == null) {
            metricnamesMap = new HashMap<String, Map<String, String>>();
            metricTypesMap.put(metricNameLabel, metricnamesMap);
        }
        Map<String, String> datasourcesMap = metricnamesMap.get(datasource);
        if (datasourcesMap == null) {
            datasourcesMap = new HashMap<String, String>();
            metricnamesMap.put(datasource, datasourcesMap);
        }
        datasourcesMap.put(name, value);
    }
}
