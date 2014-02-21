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

import net.sf.ehcache.CacheException;
import net.sf.ehcache.CacheManager;
import net.sf.ehcache.Ehcache;
import net.sf.ehcache.Element;
import net.sf.ehcache.constructs.blocking.CacheEntryFactory;
import net.sf.ehcache.constructs.blocking.SelfPopulatingCache;
import net.sourceforge.jrrd.ConsolidationFunctionType;
import net.sourceforge.jrrd.DataChunk;
import net.sourceforge.jrrd.DataSource;
import net.sourceforge.jrrd.RRDException;
import net.sourceforge.jrrd.RRDatabase;
import org.openinfinity.healthmonitoring.model.RrdValue;
import org.openinfinity.rrddatareader.InvalidResourceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Retrieves information about RRD DB structure and parses RRD DB files.
 *
 * @author kukrevit
 */
public class RrdDataParser {

    private static final Logger LOGGER = LoggerFactory.getLogger(RrdDataParser.class);

    private static final Ehcache CACHE;

    static {
        CacheManager cacheManager = CacheManager.create();
        CACHE = new SelfPopulatingCache(cacheManager.getEhcache("fsStructureCache"), new FSCacheFactory());
    }

    @SuppressWarnings("rawtypes")
    public static Map<String, List<RrdValue>> parseRrdFile(String fileName, Date startTime, Date endTime, long step, ConsolidationFunctionType consolidationFunc) {
        Map<String, List<RrdValue>> map = new HashMap<String, List<RrdValue>>();
        RRDatabase rrd = null;
        DataChunk chunk = null;
        try {
            if (new File(fileName).exists()) {
                rrd = new RRDatabase(fileName);
                chunk = rrd.getData(consolidationFunc, startTime, endTime, step);
                if (chunk != null) {
                    Map[] arrayOfMap = chunk.toArrayOfMap();
                    for (int i = 0; i < arrayOfMap.length; i++) {
                        Map m = arrayOfMap[i];
                        DataSource dataSource = rrd.getDataSource(i);
                        if (!map.containsKey(dataSource.getName())) {
                            map.put(dataSource.getName(), new ArrayList<RrdValue>());
                        }
                        for (Object key : m.keySet()) {
                            RrdValue rrdValue = new RrdValue((Date) key, (Double) m.get(key));
                            map.get(dataSource.getName()).add(rrdValue);
                        }
                    }
                }
            }
        } catch (RRDException e) {
            LOGGER.error("RRDException while parsing rrd file", e);
            map = null;
        } catch (IOException e) {
            LOGGER.error("IOException while parsing rrd file", e);
            map = null;
        } finally {
            if (rrd != null) {
                try {
                    rrd.close();
                } catch (IOException e) {
                    LOGGER.error("IOException while closing rrd file", e);
                }
            }
        }
        return map;
    }

    public static List<String> getStructure(final String basePath, final boolean onlyDirs)
            throws InvalidResourceException {
        Element element = null;
        try {
            element = CACHE.get(basePath + "#" + String.valueOf(onlyDirs));
        } catch (CacheException e) {
            if (e.getCause() instanceof InvalidResourceException) {
                throw (InvalidResourceException) e.getCause();
            }
        }
        if (element != null && element.getObjectValue() instanceof List) {
            return (List<String>) element.getObjectValue();
        }
        return null;
    }

    private static class FSCacheFactory implements CacheEntryFactory {

        @Override
        public Object createEntry(Object key) throws Exception {
            LOGGER.debug("Reading structure from FS: " + key);
            if (key != null && key instanceof String) {
                String[] parts = ((String) key).split("#");
                if (parts.length == 2) {
                    String basePath = parts[0];
                    boolean onlyDirs = Boolean.valueOf(parts[1]);
                    return getRrdDBStructure(basePath, onlyDirs);
                }
            }
            return null;
        }

        public static List<String> getRrdDBStructure(final String basePath, final boolean onlyDirs)
                throws InvalidResourceException {
            List<String> result = null;

            File baseDir = new File(basePath);
            if (baseDir.exists() && baseDir.isDirectory()) {
                result = new ArrayList<String>();
                File[] listFiles = baseDir.listFiles(new FileFilter() {

                    public boolean accept(File pathname) {
                        //ignoring hidden files
                        if (pathname.getName().startsWith(".")) {
                            return false;
                        }
                        if (onlyDirs) {
                            return pathname.isDirectory();
                        }
                        return true;
                    }
                });
                if (listFiles != null) {
                    for (File file : listFiles) {
                        result.add(file.getName());
                    }
                }
            } else {
                throw new InvalidResourceException("Resource '" + basePath + "' doesn't exist");
            }
            return result;
        }

    }
}
