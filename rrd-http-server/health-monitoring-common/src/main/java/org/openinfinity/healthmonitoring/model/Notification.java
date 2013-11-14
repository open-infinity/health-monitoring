/*
 * #%L
 * Health Monitoring : Common
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
package org.openinfinity.healthmonitoring.model;

import java.io.Serializable;

/**
 * @author kukrevit
 */
public class Notification implements Serializable {

    /**
     * serialVersionUID
     */
    private static final long serialVersionUID = -961540234666488312L;

    private static final String LINE_SEPARATOR = System.getProperty("line.separator");

    private String severity;
    private String hostName;
    private Long time;
    private String plugin;
    private String type;
    private String typeInstance;
    private String datasource;
    private Double currentValue;
    private String message;
    private Long fileModificationTime;
    private String fileName;
    private Double warningMin;
    private Double warningMax;
    private Double failureMin;
    private Double FailureMax;

    public String getSeverity() {
        return severity;
    }

    public void setSeverity(String severity) {
        this.severity = severity;
    }

    public String getHostName() {
        return hostName;
    }

    public void setHostName(String hostName) {
        this.hostName = hostName;
    }

    public Long getTime() {
        return time;
    }

    public void setTime(Long time) {
        this.time = time;
    }

    public String getPlugin() {
        return plugin;
    }

    public void setPlugin(String plugin) {
        this.plugin = plugin;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getTypeInstance() {
        return typeInstance;
    }

    public void setTypeInstance(String typeInstance) {
        this.typeInstance = typeInstance;
    }

    public String getDatasource() {
        return datasource;
    }

    public void setDatasource(String datasource) {
        this.datasource = datasource;
    }

    public Double getCurrentValue() {
        return currentValue;
    }

    public void setCurrentValue(Double currentValue) {
        this.currentValue = currentValue;
    }

    /**
     * @return the message
     */
    public String getMessage() {
        return message;
    }

    /**
     * @param message the message to set
     */
    public void setMessage(String message) {
        this.message = message;
    }

    /**
     * @return the fileModificationTime
     */
    public Long getFileModificationTime() {
        return fileModificationTime;
    }

    /**
     * @param fileModificationTime the fileModificationTime to set
     */
    public void setFileModificationTime(Long fileModificationTime) {
        this.fileModificationTime = fileModificationTime;
    }

    /**
     * @return the fileName
     */
    public String getFileName() {
        return fileName;
    }

    /**
     * @param fileName the fileName to set
     */
    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    /**
     * @return the warningMin
     */
    public Double getWarningMin() {
        return warningMin;
    }

    /**
     * @param warningMin the warningMin to set
     */
    public void setWarningMin(Double warningMin) {
        this.warningMin = warningMin;
    }

    /**
     * @return the warningMax
     */
    public Double getWarningMax() {
        return warningMax;
    }

    /**
     * @param warningMax the warningMax to set
     */
    public void setWarningMax(Double warningMax) {
        this.warningMax = warningMax;
    }

    /**
     * @return the failureMin
     */
    public Double getFailureMin() {
        return failureMin;
    }

    /**
     * @param failureMin the failureMin to set
     */
    public void setFailureMin(Double failureMin) {
        this.failureMin = failureMin;
    }

    /**
     * @return the failureMax
     */
    public Double getFailureMax() {
        return FailureMax;
    }

    /**
     * @param failureMax the failureMax to set
     */
    public void setFailureMax(Double failureMax) {
        FailureMax = failureMax;
    }

    /**
     * Formats {@link Notification} object into readable format.
     *
     * @return user friendly formated notification
     */
    public String format() {
        StringBuilder builder = new StringBuilder();
        builder.append("Severity: ").append(getSeverity()).append(LINE_SEPARATOR).append("Host: ")
                .append(getHostName()).append(LINE_SEPARATOR).append("Plugin: ").append(getPlugin())
                .append(LINE_SEPARATOR).append("Type: ").append(getType()).append(LINE_SEPARATOR)
                .append("TypeInstance: ").append(getTypeInstance()).append(LINE_SEPARATOR).append("Datasource: ")
                .append(getDatasource()).append(LINE_SEPARATOR).append("Value: ").append(getCurrentValue())
                .append(LINE_SEPARATOR).append("Time: ").append(getTime()).append(LINE_SEPARATOR);
        if (getFailureMin() != null) {
            builder.append(LINE_SEPARATOR).append("FailureMin: ").append(getFailureMin());
        }
        if (getFailureMax() != null) {
            builder.append(LINE_SEPARATOR).append("FailureMax: ").append(getFailureMax());
        }
        if (getWarningMin() != null) {
            builder.append(LINE_SEPARATOR).append("WarningMin: ").append(getWarningMin());
        }
        if (getWarningMax() != null) {
            builder.append(LINE_SEPARATOR).append("WarningMin: ").append(getWarningMax());
        }
        if (getMessage() != null) {
            builder.append(LINE_SEPARATOR).append("Message: ").append(getMessage());
        }
        return builder.toString();
    }

}
