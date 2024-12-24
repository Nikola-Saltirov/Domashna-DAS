package mk.ukim.finki.das.main.services;


import java.util.List;

public interface HistoricalService {
    List<String> getNames();

    List<String> getPrikazi();

    List<String> getVreminja();

    void getImg(String tiker, String prikaz, String interval);
}
