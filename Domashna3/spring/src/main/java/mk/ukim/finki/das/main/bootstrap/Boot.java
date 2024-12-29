package mk.ukim.finki.das.main.bootstrap;


import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class Boot {

    @PostConstruct
    public void init(){
        String flaskUrl = "http://localhost:5000/startup";

        // RestTemplate to make the GET request
        RestTemplate restTemplate = new RestTemplate();

        // Make GET request and receive response as String
        String jsonResponse = restTemplate.getForObject(flaskUrl, String.class);
        System.out.println(jsonResponse);
    }
}
