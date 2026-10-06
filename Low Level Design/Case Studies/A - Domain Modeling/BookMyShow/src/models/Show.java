package models;

import java.time.LocalDateTime;
import java.util.*;

public class Show {
    private final String id;
    private final Map<String, ShowSeat> showSeats = new HashMap<>();
    private final Screen screen;
    private final Movie movie;
    private final LocalDateTime startTime;
    private final LocalDateTime endTime;
    private final EnumMap<SeatType, Double> prices;


    public Show(String id, Screen screen, Movie movie, LocalDateTime startTime, LocalDateTime endTime, EnumMap<SeatType, Double> prices) {
        this.id = id;
        this.screen = screen;
        this.movie = movie;
        this.startTime = startTime;
        this.endTime = endTime;
        this.prices = prices;
        buildShowSeats();
    }

    private void buildShowSeats() {

        if (screen == null || screen.getSeats() == null || screen.getSeats().isEmpty()) {
            throw new RuntimeException("Screen must have at-least one seat");
        }
        for (Seat seat : screen.getSeats()) {
            String label = seat.getSeatLabel();
            this.showSeats.put(label, new ShowSeat(seat));
        }
    }

    public String getId() {
        return id;
    }


    public List<String> getShowSeatsLabels() {
        return showSeats.keySet().stream().toList();
    }

    public List<ShowSeat> getShowSeats() {
        return new ArrayList<>(showSeats.values());
    }

    public Screen getScreen() {
        return screen;
    }

    public Movie getMovie() {
        return movie;
    }

    public LocalDateTime getStartTime() {
        return startTime;
    }

    public LocalDateTime getEndTime() {
        return endTime;
    }

    public EnumMap<SeatType, Double> getPrices() {
        return prices;
    }
}
