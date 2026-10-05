package strategies.allocation;

import model.Floor;
import model.Spot;
import model.SpotSize;

import java.util.List;
import java.util.Optional;

public class BestFitStrategy implements AllocationStrategy {

    @Override
    public Optional<Spot> allocate(List<Floor> floors, SpotSize minSize) {
        for (SpotSize size : SpotSize.values()) {
            if (size.ordinal() < minSize.ordinal()) continue;   // too small, skip

            for (Floor floor : floors) {
                Optional<Spot> spot = floor.claimSpotOfSize(size);
                if (spot.isPresent()) return spot;
            }
        }
        return Optional.empty();
    }
}
