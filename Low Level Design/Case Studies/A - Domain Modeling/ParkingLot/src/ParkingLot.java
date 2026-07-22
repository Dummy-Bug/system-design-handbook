import model.Floor;
import model.SpotSize;
import strategies.pricing.PricingStrategy;

import java.util.*;

public class ParkingLot {

    private static final ParkingLot instance = new ParkingLot();
    Map<Integer, Floor> floors = new HashMap<>();
    PricingStrategy pricingStrategy;


    public static ParkingLot getInstance() {
        return instance;
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
