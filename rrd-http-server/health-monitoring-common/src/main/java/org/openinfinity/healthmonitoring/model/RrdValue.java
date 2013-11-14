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

import java.util.Date;

/**
 * @author kukrevit
 */
public class RrdValue implements Comparable<RrdValue> {
    public static final int HASH_CODE_CONST = 32;
    private long date;
    private Double value;

    /**
     * Default Constructor.
     */
    public RrdValue() {
        super();
    }

    /**
     * @param d
     *            date
     * @param value
     *            value
     */
    public RrdValue(Date d, Double value) {
        super();
        this.date = d.getTime();
        this.value = value;
    }

    public long getDate() {
        return date;
    }

    public void setDate(long date) {
        this.date = date;
    }

    public Double getValue() {
        return value;
    }

    public void setValue(Double value) {
        this.value = value;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + (int) (date ^ date >>> HASH_CODE_CONST);
        result = prime * result + (value == null ? 0 : value.hashCode());
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
        final RrdValue other = (RrdValue) obj;
        if (date != other.date) {
            return false;
        }
        if (value == null) {
            if (other.value != null) {
                return false;
            }
        } else if (!value.equals(other.value)) {
            return false;
        }
        return true;
    }
    
    public int compareTo(RrdValue a) {
        if(this.getDate() > a.getDate()){
         return 1;
        }
        else if(this.getDate() < a.getDate()){
            return 1;
        }
        return 0;
       }
}
