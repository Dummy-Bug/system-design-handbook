package strategies.allocation;

import model.Floor;
import model.Spot;
import model.SpotSize;

import java.util.Collection;
import java.util.Optional;

public class BestFitStrategy implements AllocationStrategy {

    @Override
    public Optional<Spot> allocate(Collection<Floor> floors, SpotSize minSize) {
        for (SpotSize size : SpotSize.values()) {
            if (size.ordinal() < minSize.ordinal()) continue;

            for (Floor floor : floors) {
                Optional<Spot> spot = floor.claimSpotOfSize(size);
                if (spot.isPresent()) return spot;
            }
        }
        return Optional.empty();
    }
}
