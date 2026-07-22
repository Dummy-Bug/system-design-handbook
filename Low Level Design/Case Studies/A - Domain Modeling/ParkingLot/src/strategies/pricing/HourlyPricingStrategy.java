package strategies.pricing;

import model.Ticket;

import java.time.Instant;

public class HourlyPricingStrategy implements PricingStrategy {

    private final double hourlyRate;

    public HourlyPricingStrategy(double hourlyRate) {
        this.hourlyRate = hourlyRate;
    }

    @Override
    public double calculatePrice(Ticket t, Instant exitTime) {
        return hourlyRate;
    }
}
