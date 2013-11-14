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
package org.openinfinity.healthmonitoring.http.response;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * @author kukrevit
 */
public class GroupListResponse extends AbstractResponse {

    private static final long serialVersionUID = -5761668081655876835L;

    private Map<String, Set<String>> groups = new HashMap<String, Set<String>>();

    public Map<String, Set<String>> getGroups() {
        return groups;
    }

    public void setGroups(Map<String, Set<String>> groups) {
        this.groups = groups;
    }
}
