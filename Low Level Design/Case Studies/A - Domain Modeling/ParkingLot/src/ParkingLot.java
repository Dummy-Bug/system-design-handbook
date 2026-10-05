import model.*;
import strategies.allocation.AllocationStrategy;
import strategies.allocation.BestFitStrategy;
import strategies.payment.PaymentStrategy;
import strategies.pricing.HourlyPricingStrategy;
import strategies.pricing.PricingStrategy;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ParkingLot {

    private static final ParkingLot instance = new ParkingLot();
    private final List<Floor> floors = new ArrayList<>();
    private final Map<String, Ticket> activeTickets = new ConcurrentHashMap<>();
    private PricingStrategy pricingStrategy = new HourlyPricingStrategy(100d);   // default policy
    private AllocationStrategy allocationStrategy = new BestFitStrategy();   // default policy


    public static ParkingLot getInstance() {
        return instance;
    }

    private ParkingLot() {

    }

    public void setPricingStrategy(PricingStrategy pricingStrategy) {
        this.pricingStrategy = pricingStrategy;
    }

    public void setAllocationStrategy(AllocationStrategy allocationStrategy) {
        this.allocationStrategy = allocationStrategy;
    }

    public void addFloor(Floor floor) {
        floors.add(floor);
    }

    public void displayAvailability() {
        for (Floor floor : floors) {
            System.out.print("Floor " + floor.getFloorNumber() + ": ");
            for (SpotSize size : SpotSize.values()) {
                System.out.print(size + "=" + floor.freeCount(size) + "  ");
            }
            System.out.println();
        }
    }

    public Optional<Ticket> park(Vehicle vehicle) {
        SpotSize minSize = vehicle.getType().getMinSize();
        Optional<Spot> spot = allocationStrategy.allocate(floors, minSize);
        if (spot.isEmpty()) {
            return Optional.empty();   // no compatible spot free anywhere
        }
        Ticket ticket = new Ticket(vehicle, spot.get());
        activeTickets.put(ticket.getTicketId(), ticket);
        return Optional.of(ticket);
    }

    public double unpark(String ticketId, PaymentStrategy payment) {
        Ticket ticket = activeTickets.get(ticketId);
        if (ticket == null) {
            throw new IllegalArgumentException("No active ticket: " + ticketId);
        }

        Instant now = Instant.now();
        double fee = pricingStrategy.calculatePrice(ticket, now);

        if (!payment.pay(fee)) {
            throw new IllegalStateException("Payment failed for " + ticketId);
            // spot stays OCCUPIED, ticket stays active — the car is still there
        }

        ticket.getSpot().release();
        activeTickets.remove(ticketId);
        return fee;
    }
}
