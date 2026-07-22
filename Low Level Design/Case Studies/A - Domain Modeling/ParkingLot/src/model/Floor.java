package model;

import java.util.*;

public class Floor {

    private final int floorNumber;

    private final Map<SpotSize, List<Spot>> spots = new HashMap<>();
    private final int small;
    private final int medium;
    private final int large;

    public Floor(int number, int small, int medium, int large) {
        this.floorNumber = number;
        this.small = small;
        this.medium = medium;
        this.large = large;
        addSpots();
    }

    private void addSpots() {
        addSpot(SpotSize.SMALL, small);
        addSpot(SpotSize.MEDIUM, medium);
        addSpot(SpotSize.LARGE, large);
    }

    public Map<SpotSize, Integer> freeCountsBySize() {
        Map<SpotSize, Integer> counts = new EnumMap<>(SpotSize.class);
        for (SpotSize size : SpotSize.values()) {
            int free = 0;
            for (Spot spot : spots.getOrDefault(size, List.of())) {
                if (spot.getStatus() == SpotStatus.FREE) free++;
            }
            counts.put(size, free);
        }
        return counts;
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

    // Claim a free spot of EXACTLY this size. The shared primitive both strategies build on.
    public Optional<Spot> claimSpotOfSize(SpotSize size) {
        for (Spot spot : spots.getOrDefault(size, List.of())) {
            if (spot.tryOccupy()) return Optional.of(spot);   // find + claim, atomic
        }
        return Optional.empty();
    }

    // Size-or-bigger, smallest first — used by first-fit's per-floor scan.
    public Optional<Spot> claimFreeSpot(SpotSize minSize) {
        for (SpotSize size : SpotSize.values()) {
            if (size.ordinal() < minSize.ordinal()) continue;   // too small, skip
            Optional<Spot> spot = claimSpotOfSize(size);
            if (spot.isPresent()) return spot;
        }
        return Optional.empty();
    }
}
