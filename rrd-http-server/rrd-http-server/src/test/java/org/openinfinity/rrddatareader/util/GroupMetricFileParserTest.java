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

import org.junit.Assert;
import org.junit.Test;

import java.util.List;

public class GroupMetricFileParserTest {

    @Test
    public void testGroupNames() {
        List<String> groupNames = new GroupMetricFileParser().getGroupNames();
        Assert.assertTrue(groupNames.contains("server"));
    }

    @Test
    public void testGroupMetricTypes() {
        List<String> groupTypes = new GroupMetricFileParser().getGroupMetricTypes("server");
        Assert.assertTrue(groupTypes.contains("interface-eth2"));
        Assert.assertFalse(groupTypes.contains("error_here"));
    }

    @Test
    public void testGroupMetricNames() {
        List<String> groupTypes = new GroupMetricFileParser().getGroupMetricNames("server", "interface-eth2");
        Assert.assertTrue(groupTypes.contains("if_errors.rrd"));
        Assert.assertTrue(groupTypes.contains("if_packets.rrd"));
    }
}
