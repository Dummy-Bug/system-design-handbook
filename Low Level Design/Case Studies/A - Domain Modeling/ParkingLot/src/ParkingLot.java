import model.*;
import strategies.payment.PaymentStrategy;
import strategies.pricing.PricingStrategy;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ParkingLot {

    private static final ParkingLot instance = new ParkingLot();
    Map<Integer, Floor> floors = new HashMap<>();
    Map<String, Ticket> activeTickets = new ConcurrentHashMap<>();
    PricingStrategy pricingStrategy;


    public static ParkingLot getInstance() {
        return instance;
    }

    public Optional<Ticket> park(Vehicle vehicle) {
        SpotSize minSize = vehicle.getType().getMinSize();
        for (Floor floor : floors.values()) {
            Optional<Spot> spot = floor.claimFreeSpot(minSize);
            if (spot.isPresent()) {
                Ticket ticket = new Ticket(vehicle, spot.get());
                activeTickets.put(ticket.getTicketId(), ticket);
                return Optional.of(ticket);
            }
        }
        return Optional.empty();   // no floor had a fitting spot — lot full
    }

    public double unpark(String ticketId, PaymentStrategy payment) {
        Ticket ticket = activeTickets.get(ticketId);
        if (ticket == null) {
            throw new IllegalArgumentException("No active ticket: " + ticketId);
        }

        ticket.setExitTime(Instant.now());
        double fee = pricingStrategy.calculatePrice(ticket, ticket.getExitTime());

        if (!payment.pay(fee)) {
            throw new IllegalStateException("Payment failed for " + ticketId);
            // spot stays OCCUPIED, ticket stays active — the car is still there
        }

        ticket.getSpot().release();
        activeTickets.remove(ticketId);
        return fee;
    }

    public void setPricingStrategy(PricingStrategy pricingStrategy) {
        this.pricingStrategy = pricingStrategy;
    }

    public void addFloor(Floor floor) {
        floors.put(floor.getFloorNumber(), floor);
    }

    public void displayAvailability() {
        for (Floor floor : floors.values()) {
            Map<SpotSize, Integer> counts = floor.freeCountsBySize();
            System.out.print("Floor " + floor.getFloorNumber() + ": ");
            for (SpotSize size : SpotSize.values()) {
                System.out.print(size + "=" + counts.get(size) + "  ");
            }
            System.out.println();
        }
    }
}
