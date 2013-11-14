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

import java.io.BufferedReader;
import java.io.File;
import java.io.FileFilter;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.openinfinity.healthmonitoring.model.Notification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class NotificationFileParser {
    private static final Logger LOGGER = LoggerFactory.getLogger(NotificationFileParser.class);

    private static final String FIELDS_SEPARATOR = ":";

    private static final String SENT_FILE_SUFFIX = ".sent";

    public static enum Prefix {
        SEVERITY("Severity"), TIME("Time"), HOST("Host"), PLUGIN("Plugin"), TYPE("Type"), TYPE_INSTANCE(
                "TypeInstance"), DATASOURCE("DataSource"), CURRENT_VALUE("CurrentValue"), MESSAGE("Message"),
        WARNING_MIN("WarningMin"), WARNING_MAX("WarningMax"), FAILURE_MIN("FailureMin"), FAILURE_MAX("FailureMax"),
        UNKNOWN("");

        private final String name;

        private Prefix(String name) {
            this.name = name;
        }

        public static Prefix get(String name) {
            for (Prefix prefix : values()) {
                if (prefix.name.equalsIgnoreCase(name)) {
                    return prefix;
                }
            }
            return UNKNOWN;
        }

    }

    public static List<Notification> getNotifications(final Long startTime, final Long endTime) {
        List<Notification> responses = new ArrayList<Notification>();

        FileFilter fileFilter = new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                long lastModified = pathname.lastModified();
                if (!pathname.isFile() || startTime != null && lastModified <= startTime || endTime != null
                        && lastModified > endTime) {
                    return false;
                }
                return true;
            }
        };

        List<File> notificationFiles = getNotificationFiles(fileFilter);
        for (File file : notificationFiles) {
            responses.add(parseNotificationFile(file));
        }
        return responses;
    }

    public static List<Notification> getNotSentNotifications() {
        List<Notification> notifications = new ArrayList<Notification>();
        FileFilter fileFilter = new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                return (!pathname.getName().endsWith(SENT_FILE_SUFFIX));
            }
        };
        for (File file : getNotificationFiles(fileFilter)) {
            notifications.add(parseNotificationFile(file));
        }
        return notifications;
    }

    public static void markNotificationAsSent(List<Notification> notifications) {
        String notificationsDirPath = PropertiesReader.getString("notificationFilesPath");
        for (Notification notification : notifications) {
            File f = new File(notificationsDirPath, notification.getFileName());
            if (f.exists()) {
                File renamed = new File(notificationsDirPath, f.getName() + SENT_FILE_SUFFIX);
                boolean renameresult = f.renameTo(renamed);
                if (!renameresult) {
                    LOGGER.warn("File {} could not be renamed!", f.getName());
                }
            }
        }
    }

    private static List<File> getNotificationFiles(FileFilter fileFilter) {
        List<File> result = new ArrayList<File>();
        String notificationsDirPath = PropertiesReader.getString("notificationFilesPath");
        File notificationsDir = new File(notificationsDirPath);
        if (notificationsDir.exists() && notificationsDir.isDirectory()) {
            File[] listFiles = notificationsDir.listFiles(fileFilter);
            result = Arrays.asList(listFiles);
        }
        return result;
    }

    private static Notification parseNotificationFile(File file) {
        Notification notification = new Notification();
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(file));
            for (String line = reader.readLine(); line != null; line = reader.readLine()) {
                String value = null;
                if (line.split(FIELDS_SEPARATOR, 2).length > 1) {
                    value = line.split(FIELDS_SEPARATOR, 2)[1];
                }
                Prefix prefix = Prefix.get(line.split(FIELDS_SEPARATOR, 2)[0]);
                switch (prefix) {
                    case SEVERITY:
                        notification.setSeverity(value);
                        break;
                    case HOST:
                        notification.setHostName(value);
                        break;
                    case PLUGIN:
                        notification.setPlugin(value);
                        break;
                    case CURRENT_VALUE:
                        notification.setCurrentValue(parseDouble(value));
                        break;
                    case DATASOURCE:
                        notification.setDatasource(value);
                        break;
                    case TIME:
                        // the value in file is in seconds
                        Double dValue = parseDouble(value) * 1000;
                        notification.setTime(dValue.longValue());
                        break;
                    case TYPE:
                        notification.setType(value);
                        break;
                    case TYPE_INSTANCE:
                        notification.setTypeInstance(value);
                        break;
                    case MESSAGE:
                        notification.setMessage(value);
                        break;
                    case WARNING_MIN:
                        notification.setWarningMin(parseDouble(value));
                        break;
                    case FAILURE_MIN:
                        notification.setFailureMin(parseDouble(value));
                        break;
                    case FAILURE_MAX:
                        notification.setFailureMax(parseDouble(value));
                        break;
                    case WARNING_MAX:
                        notification.setWarningMax(parseDouble(value));
                        break;
                    default:
                        break;
                }
            }
            notification.setFileModificationTime(file.lastModified());
            notification.setFileName(file.getName());
        } catch (IOException e) {
            LOGGER.error("IOException while parsing notification file", e);
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    LOGGER.error("IOException while closing notification file", e);
                }
            }
        }
        return notification;
    }
    
    private static double parseDouble(String value) {
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException e) {
            LOGGER.warn("Couldn't convert {} into double, falling back to 0.0", value);
        }
        return 0.0;
    }
}
