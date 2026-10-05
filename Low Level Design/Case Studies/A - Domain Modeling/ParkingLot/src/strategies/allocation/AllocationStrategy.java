package strategies.allocation;

import model.Floor;
import model.Spot;
import model.SpotSize;

import java.util.List;
import java.util.Optional;

public interface AllocationStrategy {

    // Returns a spot it has ALREADY claimed (occupied), or empty if none fits.
    Optional<Spot> allocate(List<Floor> floors, SpotSize minSize);
}
