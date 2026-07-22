package model;

import java.util.*;

public class Floor {

    private final int floorNumber;

    private final Map<SpotSize, List<Spot>> spots = new HashMap<>();

    public Floor(int number, int small, int medium, int large) {
        this.floorNumber = number;
        addSpots(small, medium, large);
    }

    private void addSpots(int small, int medium, int large) {
        addSpot(SpotSize.SMALL, small);
        addSpot(SpotSize.MEDIUM, medium);
        addSpot(SpotSize.LARGE, large);
    }

    public int getFloorNumber() {
        return floorNumber;
    }

    public void addSpot(SpotSize size, int count) {
        List<Spot> list = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            list.add(new Spot(floorNumber + "-" + size + "-" + i, size));
        }
        spots.put(size, list);
    }

    private Optional<Spot> getFreeSpot(SpotSize minSize) {

        for (SpotSize size : SpotSize.values()) {
            if (size.ordinal() < minSize.ordinal()) continue;

            for (Spot spot : spots.getOrDefault(minSize, List.of()))
                if (spot.getStatus() == SpotStatus.FREE) return Optional.of(spot);
        }
        return Optional.empty();

    }
}
