package mk.ukim.finki.das.main.services.impl;


import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import mk.ukim.finki.das.main.services.HistoricalService;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;

import org.springframework.web.client.RestTemplate;

@Service
public class HistoricalServiceImpl implements HistoricalService {

    private final RestTemplate restTemplate;

    public HistoricalServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Override
    public List<String>getNames() {
        String flaskUrl = "http://localhost:5000/get_names";

        // RestTemplate to make the GET request
        RestTemplate restTemplate = new RestTemplate();

        try {
            // Make GET request and receive response as String
            String jsonResponse = restTemplate.getForObject(flaskUrl, String.class);

            // Convert JSON string to List<String>
            ObjectMapper objectMapper = new ObjectMapper();
            List<String> strings = objectMapper.readValue(jsonResponse, new TypeReference<List<String>>() {});

            // Process the received strings
            System.out.println("Received strings from Flask: " + strings);

            // Return success response
            return strings;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return List.of();
    }

    @Override
    public List<String> getPrikazi() {
        List<String> prikazi = new ArrayList<>();
        prikazi.add("Awesome Oscillator");
        prikazi.add("DeMarket Indicator");
        prikazi.add("Commodity Channel Index");
        prikazi.add("Chande Momentum Oscillator");
        prikazi.add("Stochastic Oscillator");
        prikazi.add("Relative Strength Index");
        prikazi.add("Simple Moving Average");
        prikazi.add("Exponential Moving Average");
        prikazi.add("Weighted Moving Average");
        prikazi.add("Smoothed Moving Average");
        prikazi.add("Volume Weighted Moving Average");
        return prikazi;
    }

    @Override
    public List<String> getVreminja() {
        List<String> vreminja = new ArrayList<>();
        vreminja.add("7 Days");
        vreminja.add("14 Days");
        vreminja.add("30 Days");
        vreminja.add("60 Days");
        vreminja.add("120 Days");
        vreminja.add("180 Days");
        return vreminja;
    }

    @Override
    public void getImg(String tiker, String prikaz, String interval) {
        String flaskUrl = "http://localhost:5000/get_image";
//        tiker=data['tiker']
//        interval=data['interval']
//        prikaz = data['prikaz']
        String jsonBody = String.format("{\"tiker\": \"%s\", \"interval\": %s}, \"prikaz\": %s}", tiker, interval, prikaz);
        ResponseEntity<Resource> response = restTemplate.exchange(
                flaskUrl,
                HttpMethod.POST,
                null,
                Resource.class
        );
        StringBuilder stringBuilder=new StringBuilder();
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            try (InputStream inputStream = response.getBody().getInputStream()) {
                // Save the image to a file
                Path outputPath = Paths.get("src/main/resources/static/img/image_from_flask.png");
                Files.createDirectories(outputPath.getParent());
                Files.copy(inputStream, outputPath, StandardCopyOption.REPLACE_EXISTING);
                stringBuilder.append("/img/image_from_flask.png");
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("Failed to fetch the image. Status: " + response.getStatusCode());
        }
    }
}
