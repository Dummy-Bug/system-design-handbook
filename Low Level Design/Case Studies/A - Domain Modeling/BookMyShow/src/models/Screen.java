package models;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Screen {
    private final String id;

    private final Map<String, Seat> seatLayout = new HashMap<>();

    public Screen(String id, List<Seat> seats) {
        this.id = id;
        buildSeatLayout(seats);
    }

    public String getId() {
        return id;
    }

    private void buildSeatLayout(List<Seat> seats) {
        for (Seat seat : seats) {
            if (seat != null) {
                if (!seatLayout.containsKey(seat.getSeatLabel())) {
                    seatLayout.put(seat.getSeatLabel(), seat);
                }
                else{
                    throw new RuntimeException(seat.getSeatLabel() + " Seat already exists");
                }
            }

        }
    }

    public List<String> getAllSeatLabels() {
        return seatLayout.keySet().stream().toList();
    }

    public List<Seat> getSeats() {
        return new ArrayList<>(seatLayout.values());
    }
}
