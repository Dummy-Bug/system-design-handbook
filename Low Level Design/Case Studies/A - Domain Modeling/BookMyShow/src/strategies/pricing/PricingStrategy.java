package strategies.pricing;

import models.SeatType;
import models.Show;

import java.util.EnumMap;

public interface PricingStrategy {

    EnumMap<SeatType, Double> apply(Show show, EnumMap<SeatType, Double> prices);
}
