package strategies.pricing;

import models.SeatType;
import models.Show;

import java.time.LocalTime;
import java.util.EnumMap;

public class MorningDiscountPricing implements PricingStrategy {

    private static final LocalTime NOON = LocalTime.NOON;

    private final double discountPercentage;

    public MorningDiscountPricing(double discountPercentage) {
        this.discountPercentage = discountPercentage;
    }

    @Override
    public EnumMap<SeatType, Double> apply(Show show, EnumMap<SeatType, Double> prices) {
        if (!show.getStartTime().toLocalTime().isBefore(NOON)) {
            return prices;
        }

        EnumMap<SeatType, Double> discounted = new EnumMap<>(SeatType.class);
        for (SeatType type : prices.keySet()) {
            double price = prices.get(type);
            discounted.put(type, price - price * discountPercentage / 100);
        }
        return discounted;
    }
}
