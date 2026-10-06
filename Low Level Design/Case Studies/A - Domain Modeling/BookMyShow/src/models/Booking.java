package models;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.EnumMap;
import java.util.List;

public class Booking {
    private final String id;
    private final Show show;
    private final User user;

    private List<ShowSeat> seats;
    private BookingStatus status;
    private double amount;
    private Instant expiresAt;

    public Booking(String id, Show show, List<ShowSeat> seats, User user) {
        this.id = id;
        this.show = show;
        this.seats = seats;
        this.user = user;
        this.status = BookingStatus.PENDING;
        this.expiresAt = Instant.now().plus(5L, ChronoUnit.MINUTES);
        calculateAmount();
    }

    private void calculateAmount() {
        EnumMap<SeatType, Double> prices = this.show.getPrices();

        for (ShowSeat showSeat : seats) {
            SeatType type = showSeat.getSeat().getSeatType();
            this.amount += prices.get(type);
        }
    }

    public BookingStatus getStatus() {
        return status;
    }

    public double getAmount() {
        return amount;
    }

    public Instant getExpiresAt() {
        return expiresAt;
    }

    public void setStatus(BookingStatus status) {
        this.status = status;
    }
}
