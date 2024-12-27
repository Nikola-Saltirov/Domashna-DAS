package mk.ukim.finki.das.main.web.controller;


import mk.ukim.finki.das.main.services.PredictionService;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Controller
@RequestMapping("/projections")
public class projectionController {

    private final String FLASK_IMAGE_PROJECTIONS_URL = "http://localhost:5000/generate-image-projections";
    private final RestTemplate restTemplate;
    private final PredictionService predictionService;

    public projectionController(RestTemplate restTemplate, PredictionService predictionService) {
        this.restTemplate = restTemplate;
        this.predictionService = predictionService;
    }

    @GetMapping
    public String getProjectionsPage(Model model) {
//        String value="/img/tmp1.png";
        List<String> tikeri = predictionService.getNames();
        model.addAttribute("defaultInterval", 7);
        model.addAttribute("intervals", List.of(7,14,30,210));
        model.addAttribute("names", tikeri);
        model.addAttribute("defaultName", tikeri.get(0));
//        model.addAttribute("imageID", value);
        return "projections";
    }
}
