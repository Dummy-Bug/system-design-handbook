import model.Floor;
import model.Ticket;
import model.Vehicle;
import model.VehicleType;
import strategies.payment.CashPaymentStrategy;
import strategies.pricing.HourlyPricingStrategy;

import java.util.Optional;


public class Application {

    public static void main(String[] args) {

        ParkingLot lot = ParkingLot.getInstance();

        lot.setPricingStrategy(new HourlyPricingStrategy(100d));

        Floor f1 = new Floor(1,1,3,2);   // only 1 small spot on floor 1 → forces fallthrough
        Floor f2 = new Floor(2,2,3,4);

        lot.addFloor(f1);
        lot.addFloor(f2);

        Vehicle bike = new Vehicle("KA-1234", VehicleType.BIKE);

        lot.displayAvailability();

        Optional<Ticket> parked = lot.park(bike);
        if (parked.isEmpty()) {
            System.out.println("Lot full");
            return;
        }
        Ticket t = parked.get();
        System.out.println(t.getTicketId() + " -> " + t.getSpot().getId());
        lot.displayAvailability();

        double fee = lot.unpark(t.getTicketId(), new CashPaymentStrategy());
        System.out.println("Paid: " + fee);

        lot.displayAvailability();

        // --- FR3: fallthrough — a bike takes a car spot only when no bike spot is free ---
        System.out.println("\n--- fallthrough (first-fit) ---");
        for (int i = 1; i <= 2; i++) {
            Optional<Ticket> p = lot.park(new Vehicle("BIKE-" + i, VehicleType.BIKE));
            if (p.isPresent()) {
                System.out.println("BIKE-" + i + " -> " + p.get().getSpot().getId());
            } else {
                System.out.println("BIKE-" + i + " -> no spot");
            }
        }

        // --- FR7: full lot rejects cleanly (Optional.empty, not an exception) ---
        System.out.println("\n--- full-lot rejection ---");
        int count = 0;
        while (lot.park(new Vehicle("FILL-" + count, VehicleType.BIKE)).isPresent()) {
            count++;   // bikes fall through to bigger spots, so this fills the whole lot
        }
        System.out.println("Parked " + count + " more, lot now full");

        Optional<Ticket> overflow = lot.park(new Vehicle("OVERFLOW", VehicleType.CAR));
        System.out.println("One more vehicle -> " +
                (overflow.isPresent() ? overflow.get().getSpot().getId() : "REJECTED (lot full)"));
    }

}
