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

import org.codehaus.jackson.JsonGenerator;
import org.codehaus.jackson.JsonProcessingException;
import org.codehaus.jackson.map.SerializerProvider;
import org.codehaus.jackson.map.ser.std.ScalarSerializerBase;

import java.io.IOException;
import java.text.DecimalFormat;

/**
 * Custom double serializer. Outputs double value in default format (not
 * scientific)
 *
 * @author kukrevit
 */
public class CustomDoubleSerializer extends ScalarSerializerBase<Double> {
    private static final DecimalFormat DECIMAL_FORMAT = new DecimalFormat("###.###");

    protected CustomDoubleSerializer(final Class<Double> t) {
        super(t);
    }

    public CustomDoubleSerializer() {
        this(Double.class);
    }

    @Override
    public void serialize(final Double value, final JsonGenerator jgen,
                          final SerializerProvider provider) throws IOException, JsonProcessingException {
        if (value != null && !value.equals(Double.NaN)) {
            jgen.writeString(DECIMAL_FORMAT.format(value.doubleValue()));
        } else {
            jgen.writeString(String.valueOf(Double.NaN));
        }
    }
}
