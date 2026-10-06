package models;

import java.time.Instant;

public class ShowSeat {
    private final Seat seat;
    private ShowSeatStatus status;
    private User lockedBy;
    private Instant lockedAt;

    public ShowSeat(Show show, Seat seat, ShowSeatStatus status) {
        this.seat = seat;
        this.status = status;
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

    public void setLockedBy(User user) {
        this.lockedBy = user;
    }

    public User getLockedBy() {
        return lockedBy;
    }

}
