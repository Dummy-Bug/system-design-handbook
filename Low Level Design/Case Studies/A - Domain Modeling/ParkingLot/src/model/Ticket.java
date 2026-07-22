package model;

import java.time.Instant;

public class Ticket {

    private String ticketId;
    private String plate;

    Spot spot;

    Instant entryTime;
    Instant exitTime;

    public String getTicketId() {
        return ticketId;
    }

    public Spot getSpot() {
        return spot;
    }

    public Instant getExitTime() {
        return exitTime;
    }

    public Instant getEntryTime() {
        return entryTime;
    }
}
