package mk.ukim.finki.das.main.spring.web.controller;


import mk.ukim.finki.das.main.spring.services.HistoricalService;
import mk.ukim.finki.das.main.spring.services.impl.HistoricalServiceImpl;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
@RequestMapping("/history")
public class historicalController {

    private final HistoricalService historicalServiceImpl;

    public historicalController(HistoricalServiceImpl historicalServiceImpl) {
        this.historicalServiceImpl = historicalServiceImpl;
    }

    @GetMapping
    public String getHistoryPage(Model model) {
        List<String> options=historicalServiceImpl.getNames();
        String defaultOption= options.get(0);
        List<String> prikazi=historicalServiceImpl.getPrikazi();
        String defaulPrikazi="SMA";
        List<String> vreminja=historicalServiceImpl.getVreminja();
        String defaulVreme=prikazi.get(0);
//        String value="/img/tmp1.png";
        model.addAttribute("options", options);
        model.addAttribute("default", defaultOption);
        model.addAttribute("prikazi", prikazi);
        model.addAttribute("defaultPrikaz", defaulPrikazi);
        model.addAttribute("vreminja", vreminja);
        model.addAttribute("defaultVreme", defaulVreme);
//        model.addAttribute("imageID", value);
        return "history";
    }

}
