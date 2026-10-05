package model;

import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

public class Ticket {

    private static final AtomicLong COUNTER = new AtomicLong(1);

    private final String ticketId;
    private final Vehicle vehicle;
    private final Spot spot;
    private final Instant entryTime;

    public Ticket(Vehicle vehicle, Spot spot) {
        this.ticketId = "T-" + COUNTER.getAndIncrement();
        this.vehicle = vehicle;
        this.spot = spot;
        this.entryTime = Instant.now();
    }

    public String getTicketId() {
        return ticketId;
    }

    public Vehicle getVehicle() {
        return vehicle;
    }

    public Spot getSpot() {
        return spot;
    }

    public Instant getEntryTime() {
        return entryTime;
    }
}
