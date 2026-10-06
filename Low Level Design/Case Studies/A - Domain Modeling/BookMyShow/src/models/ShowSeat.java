package models;


public class ShowSeat {
    private final Seat seat;
    private ShowSeatStatus status;
    private Booking lockedBy;

    public ShowSeat(Seat seat) {
        this.seat = seat;
        this.status = ShowSeatStatus.FREE;
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
        return status;
    }

    public void setStatus(ShowSeatStatus status) {
        this.status = status;
    }

    public void setLockedBy(Booking booking) {
        this.lockedBy = booking;
    }


}
