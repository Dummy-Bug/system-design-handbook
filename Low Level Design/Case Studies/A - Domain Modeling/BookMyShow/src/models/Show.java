package models;

import java.time.LocalDateTime;
import java.util.List;

public class Show {
    String id;
    List<ShowSeat> showSeats;
    Screen screen;
    Movie movie;
    LocalDateTime startTime;
    LocalDateTime endTime;
}
