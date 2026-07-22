package strategies.allocation;

import model.Floor;
import model.Spot;
import model.SpotSize;

import java.util.Collection;
import java.util.Optional;

// First floor that has any fitting spot wins; within a floor, smallest fitting size.
// Prefers same-floor over walking to another floor.
public class FirstFitStrategy implements AllocationStrategy {

    @Override
    public Optional<Spot> allocate(Collection<Floor> floors, SpotSize minSize) {
        for (Floor floor : floors) {
            Optional<Spot> spot = floor.claimFreeSpot(minSize);
            if (spot.isPresent()) return spot;
        }
        return Optional.empty();
    }
}
