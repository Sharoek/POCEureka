/*
   Copyright 2013, 2016-2020 Nationale-Nederlanden, 2020-2025 WeAreFrank!

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
package org.frankframework.eureka;

import org.frankframework.util.DomBuilderException;
import org.frankframework.util.XmlUtils;
import org.springframework.web.client.RestClient;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

public class EurekaRESTClient {
    private static final String SERVER_URL = "http://localhost:8761";
    private static RestClient client;

    private static void initClient() {
        if (client == null) {
            client = RestClient.create();
        }
    }
    
    public static String getServiceByName(String appID){
        initClient();
        return client.get()
        .uri(SERVER_URL + "/eureka/apps/" + appID)
        .retrieve()
        .body(String.class); 
    }

    public static String getHomePageUrl(String appID){
        String response = getServiceByName(appID);
        try {
            Document doc = XmlUtils.buildDomDocument(response);
            Element root = doc.getDocumentElement();
            NodeList instanceList = root.getElementsByTagName("instance");
            if (instanceList.getLength() > 0) {
                Element instanceElement = (Element) instanceList.item(0);
                String homePageUrl = XmlUtils.getChildTagAsString(instanceElement, "homePageUrl");
                return homePageUrl;
            }
        } catch (DomBuilderException e) {
            e.printStackTrace();
        }
        return null;
    }
}
