package model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;

public class Floor {

    private final int floorNumber;

    private final Map<SpotSize, List<Spots>> spots = new HashMap<>();

    public Floor(int number, int small, int medium, int large) {
        this.floorNumber = number;

    }

    public int getFloorNumber() {
        return floorNumber;
    }

    private void addSpot(SpotSize size, int count) {
        List<Spot> list = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            list.add(new Spot(floorNumber + "-" + size + "-" + i));
        }
        spots.put(size, list);
    }
}
