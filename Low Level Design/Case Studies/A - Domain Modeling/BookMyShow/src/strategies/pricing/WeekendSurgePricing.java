package strategies.pricing;

import models.SeatType;
import models.Show;

import java.time.DayOfWeek;
import java.util.EnumMap;

public class WeekendSurgePricing implements PricingStrategy {

    private final double surgePercentage;

    public WeekendSurgePricing(double surgePercentage) {
        this.surgePercentage = surgePercentage;
    }

    @Override
    public EnumMap<SeatType, Double> apply(Show show, EnumMap<SeatType, Double> prices) {
        DayOfWeek day = show.getStartTime().getDayOfWeek();
        if (day != DayOfWeek.SATURDAY && day != DayOfWeek.SUNDAY) {
            return prices;
        }

        EnumMap<SeatType, Double> surged = new EnumMap<>(SeatType.class);
        for (SeatType type : prices.keySet()) {
            double price = prices.get(type);
            surged.put(type, price + price * surgePercentage / 100);
        }
        return surged;
    }
}
