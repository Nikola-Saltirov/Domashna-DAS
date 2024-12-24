package mk.ukim.finki.das.main.web.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class restMainController {

    private final RestTemplate restTemplate;

    private final String FLASK_IMAGE_URL = "http://localhost:5000/generate-image";

    public restMainController(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @GetMapping("/get-flask-image")
    @ResponseBody
    public byte[] getImageFromFlask(@RequestParam String tiker, @RequestParam String interval, @RequestParam String prikaz) {
        String flaskUrlWithParams = FLASK_IMAGE_URL + "?tiker=" + tiker + "&interval=" + interval + "&prikaz=" + prikaz;

        ResponseEntity<byte[]> response = restTemplate.getForEntity(flaskUrlWithParams, byte[].class);

        return response.getBody();
    }
}
