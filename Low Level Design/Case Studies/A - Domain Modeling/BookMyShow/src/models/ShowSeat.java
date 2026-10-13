package models;


public class ShowSeat {
    private final Seat seat;
    private Booking lockedBy;

    public ShowSeat(Seat seat) {
        this.seat = seat;
    }

    public Seat getSeat() {
        return seat;
    }

    public Booking getLockedBy() {
        return lockedBy;
    }

    public String getShowSeatLabel() {
        return seat.getSeatLabel();
    }

    public ShowSeatStatus getStatus() {
        if (lockedBy == null) {
            return ShowSeatStatus.FREE;
        }
        if (lockedBy.getStatus().equals(BookingStatus.CONFIRMED)) {
            return ShowSeatStatus.BOOKED;
        }
        if (lockedBy.isHoldActive()) {
            return ShowSeatStatus.LOCKED;
        }
        return ShowSeatStatus.FREE;
    }

    public void setLockedBy(Booking booking) {
        this.lockedBy = booking;
    }


}
