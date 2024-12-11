package mk.ukim.finki.das.main.web.controller;


import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.ArrayList;
import java.util.List;

@Controller
@RequestMapping("/projections")
public class projectionController {

    @GetMapping
    public String getProjectionsPage(Model model) {
        String value="/img/tmp1.png";
        List<String> options=new ArrayList<String>();
        options.add("tmp1");
        options.add("tmp2");
        options.add("tmp3");
        String defaultValue="tmp1";
        model.addAttribute("default", defaultValue);
        model.addAttribute("options", options);
        model.addAttribute("imageID", value);
        return "projections";
    }

    @PostMapping
    public String getProjections(@RequestParam String tiker, @RequestParam String prikaz, @RequestParam String interval, Model model) {
        String path="/img/"+tiker+".png";
        List<String> options=new ArrayList<String>();
        options.add("tmp1");
        options.add("tmp2");
        options.add("tmp3");
        model.addAttribute("default", tiker);
        model.addAttribute("options", options);
        model.addAttribute("imageID", path);
        return "projections";
    }
}
