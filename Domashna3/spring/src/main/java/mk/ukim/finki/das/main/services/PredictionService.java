package mk.ukim.finki.das.main.services;

import java.util.List;

public interface PredictionService {

    List<String> getNames();
    List<String> getTimerIntervals();
    void getProjections(String tiker, String interval);

}
