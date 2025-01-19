package mk.ukim.finki.das.main.spring.bootstrap;


import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class Boot {

    @PostConstruct
    public void init(){
        String flaskUrl = "http://python:5000/startup";
        RestTemplate restTemplate = new RestTemplate();
        String jsonResponse = restTemplate.getForObject(flaskUrl, String.class);
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            JsonNode jsonNode = objectMapper.readTree(jsonResponse);
            if (jsonNode.has("FinishTime")) {
                float finishTime = (float) jsonNode.get("FinishTime").asDouble();
                System.out.printf("Scraping time: %.2f minutes\n", finishTime);
            } else {
                System.out.println("FinishTime field not found in JSON.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
