package models;

import java.time.LocalDateTime;
import java.util.EnumMap;
import java.util.List;

public class Booking {
    private final String id;
    private final Show show;
    private final User user;

    private final List<ShowSeat> seats;
    private BookingStatus status;
    private double amount;
    private final LocalDateTime expiresAt;

    public Booking(String id, Show show, List<ShowSeat> seats, User user) {
        this.id = id;
        this.show = show;
        this.seats = seats;
        this.user = user;
        this.status = BookingStatus.PENDING;
        LocalDateTime holdEndsAt = LocalDateTime.now().plusMinutes(5);
        LocalDateTime bookingClosesAt = show.getBookingClosesAt();
        this.expiresAt = holdEndsAt.isBefore(bookingClosesAt) ? holdEndsAt : bookingClosesAt;
        calculateAmount();
    }

    private void calculateAmount() {
        EnumMap<SeatType, Double> prices = this.show.getPrices();

        for (ShowSeat showSeat : seats) {
            SeatType type = showSeat.getSeat().getSeatType();
            this.amount += prices.get(type);
        }
    }

    public boolean isHoldActive() {
        return status.equals(BookingStatus.PENDING) && LocalDateTime.now().isBefore(expiresAt);
    }

    public List<ShowSeat> getShowSeats() {
        return seats;
    }

    public Show getShow() {
        return show;
    }

    public BookingStatus getStatus() {
        return status;
    }

    public double getAmount() {
        return amount;
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setStatus(BookingStatus status) {
        this.status = status;
    }
}
