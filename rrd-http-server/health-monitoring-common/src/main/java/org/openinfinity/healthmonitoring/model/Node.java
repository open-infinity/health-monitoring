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
 * Information about node. This class has a natural ordering that is inconsistent with equals.
 * 
 * @author kukrevit
 * @author Vedran Bartonicek
 */
public class Node implements Serializable, Comparable<Node> {

    /**
     * Serial version UID.
     */
    private static final long serialVersionUID = -8894540143071283517L;

    private String ipAddress;

    private String nodeName;

    private String groupName;
    
    //private String machineType;

    public String getIpAddress() {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }

    public String getNodeName() {
        return nodeName;
    }
    
    public void setNodeName(String nodeName) {
        this.nodeName = nodeName;
    }

    public String getGroupName() {
        return groupName;
    }

    public void setGroupName(String groupName) {
        this.groupName = groupName;
    }

    /*
    public String getMachineType() {
        return machineType;
    }

    public void setMachineType(String machineType) {
        this.machineType = machineType;
    }
    */
    
    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((groupName == null) ? 0 : groupName.hashCode());
        result = prime * result + ((ipAddress == null) ? 0 : ipAddress.hashCode());
        result = prime * result + ((nodeName == null) ? 0 : nodeName.hashCode());
        //result = prime * result + ((machineType == null) ? 0 : machineType.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final Node other = (Node) obj;
        if (groupName == null) {
            if (other.groupName != null) {
                return false;
            }
        } else if (!groupName.equals(other.groupName)) {
            return false;
        }
        if (ipAddress == null) {
            if (other.ipAddress != null) {
                return false;
            }
        } else if (!ipAddress.equals(other.ipAddress)) {
            return false;
        }
        /*
        if (machineType == null) {
            if (other.machineType != null) {
                return false;
            }
        } else if (!machineType.equals(other.machineType)) {
            return false;
        }
        */
        if (nodeName == null) {
            if (other.nodeName != null) {
                return false;
            }
        } else if (!nodeName.equals(other.nodeName)) {
            return false;
        }
        return true;
    }

    @Override
    public int compareTo(Node o) {
        return this.nodeName.compareTo(o.nodeName);
    }

}
