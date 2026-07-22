import model.Floor;
import model.Ticket;
import model.Vehicle;
import model.VehicleType;
import strategies.payment.CashPaymentStrategy;
import strategies.pricing.HourlyPricingStrategy;


public class Application {

    public static void main(String[] args) {

        ParkingLot lot = ParkingLot.getInstance();

        lot.setPricingStrategy(new HourlyPricingStrategy(100));

        Floor f1 = new Floor(1,4,3,2);
        Floor f2 = new Floor(2,2,3,4);

        lot.addFloor(f1);
        lot.addFloor(f2);

        Vehicle bike = new Vehicle("KA-1234", VehicleType.BIKE);

        lot.displayAvailability();
        Ticket t = lot.park(bike);
        System.out.println(t.getTicketId() + " -> " + t.getSpot().getId());
        lot.displayAvailability();

        double fee = lot.unpark(t.getTicketId(), new CashPaymentStrategy());
        System.out.println("Paid: " + fee);

        lot.displayAvailability();


    }

}
