import model.Floor;

import java.util.HashMap;
import java.util.Map;

public class ParkingLot {

    private static final ParkingLot instance = new ParkingLot();
    Map<Integer, Floor> floors = new HashMap<>();

    public static ParkingLot getInstance() {
        return instance;
    }

    public void addFloor(Floor floor) {
        floors.put(floor.getFloorNumber(), floor);
    }
}
