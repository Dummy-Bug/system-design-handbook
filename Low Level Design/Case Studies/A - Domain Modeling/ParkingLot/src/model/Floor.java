package model;

import java.util.*;

public class Floor {

    private final int floorNumber;

    private final List<Spot> spots = new ArrayList<>();

    public Floor(int number, int small, int medium, int large) {
        this.floorNumber = number;
        addSpots(SpotSize.SMALL, small);
        addSpots(SpotSize.MEDIUM, medium);
        addSpots(SpotSize.LARGE, large);
    }

    private void addSpots(SpotSize size, int count) {
        for (int i = 0; i < count; i++) {
            spots.add(new Spot(floorNumber + "-" + size + "-" + i, size));
        }
    }

    public int freeCount(SpotSize size) {
        int free = 0;
        for (Spot spot : spots) {
            if (spot.getSize() == size && spot.getStatus() == SpotStatus.FREE) free++;
        }
        return free;
    }

    public int getFloorNumber() {
        return floorNumber;
    }

    // Claim a free spot of EXACTLY this size.
    public Optional<Spot> claimSpotOfSize(SpotSize size) {
        for (Spot spot : spots) {
            if (spot.getSize() == size && spot.tryOccupy()) return Optional.of(spot);   // find + claim, atomic
        }
        return Optional.empty();
    }
}
