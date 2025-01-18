package mk.ukim.finki.das.main.spring.web.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/get-flask-image")
public class restMainController {

    private final RestTemplate restTemplate;

    private final String FLASK_IMAGE_HISTORY_URL = "http://localhost:5000/generate-image-history";

    private final String FLASK_IMAGE_PROJECTIONS_URL = "http://localhost:5000/generate-image-projections";

    public restMainController(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @GetMapping("/history")
    @ResponseBody
    public byte[] getImageFromFlask(@RequestParam String tiker, @RequestParam String interval, @RequestParam String prikaz) {
         String flaskUrlWithParams = FLASK_IMAGE_HISTORY_URL + "?tiker=" + tiker + "&interval=" + interval + "&prikaz=" + prikaz;

        ResponseEntity<byte[]> response = restTemplate.getForEntity(flaskUrlWithParams, byte[].class);

        return response.getBody();
    }
    @GetMapping("/projections")
    @ResponseBody
    public byte[] getImageProjectionsFromFlask(@RequestParam String tiker, @RequestParam String interval) {
        String flaskUrlWithParams = FLASK_IMAGE_PROJECTIONS_URL + "?tiker=" + tiker + "&interval=" + interval;

        ResponseEntity<byte[]> response = restTemplate.getForEntity(flaskUrlWithParams, byte[].class);

        return response.getBody();
    }
}
