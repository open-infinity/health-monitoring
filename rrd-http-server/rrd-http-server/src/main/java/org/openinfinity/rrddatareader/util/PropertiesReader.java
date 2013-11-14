/*
 * #%L
 * Health Monitoring : RRD Data Reader
 * %%
 * Copyright (C) 2013 Tieto
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

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PropertiesReader {

    private static final String ENV_VARIABLE_END = "}";
    private static final String ENV_VARIABLE_START = "{";

    private static final String TOAS_VARIABLE_MATCHER = ".*\\" + ENV_VARIABLE_START + "TOAS.*\\" + ENV_VARIABLE_END
            + ".*";

    private static final Logger LOGGER = LoggerFactory.getLogger(PropertiesReader.class);

    private static final Properties PROPERTIES;

    static {
        InputStream is = PropertiesReader.class.getResourceAsStream("/rrddatareader.properties");
        PROPERTIES = new Properties();
        try {
            PROPERTIES.load(is);
        } catch (IOException e) {
            LOGGER.error("Error while loading properties", e);
        } finally {
            try {
                if (is != null) {
                    is.close();
                }
            } catch (IOException e) {
                LOGGER.error("IOException while closing properties IS", e);
            }
        }
    }

    public static String getString(String key) {
        return get(key);
    }

    public static Integer getInteger(String key) {
        return Integer.valueOf(get(key));
    }

    private static String get(String key) {
        String property = PROPERTIES.getProperty(key);
        if (property != null && property.matches(TOAS_VARIABLE_MATCHER)) {
            property = EnvVariableSubstitutor.replace(property);
            PROPERTIES.put(key, property);
        }
        return property;
    }

    private static class EnvVariableSubstitutor {

        public static String replace(String value) {
            int start = value.indexOf(ENV_VARIABLE_START);
            int end = value.indexOf(ENV_VARIABLE_END);
            if (start != -1 && end != -1 && start + 1 < end) {
                String var = value.substring(start + 1, end);
                String envVar = System.getenv(var);
                if (envVar == null) {
                    envVar = "";
                }
                value = value.replace(ENV_VARIABLE_START + var + ENV_VARIABLE_END, envVar);
            }
            return value.matches(TOAS_VARIABLE_MATCHER) ? replace(value) : value;
        }
    }

    public static void main(String... args) throws IOException {
        System.out.println(EnvVariableSubstitutor.replace("{TOAS_VAR_1}/{TOAS_VAR_2}/memory"));
        System.out.println(EnvVariableSubstitutor.replace("/opt/memory"));
    }
}
