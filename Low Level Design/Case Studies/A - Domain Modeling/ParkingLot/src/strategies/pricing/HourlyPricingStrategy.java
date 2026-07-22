package strategies.pricing;

import model.Ticket;

import java.time.Duration;
import java.time.Instant;

public class HourlyPricingStrategy implements PricingStrategy {

    private final double hourlyRate;

    public HourlyPricingStrategy(double hourlyRate) {
        this.hourlyRate = hourlyRate;
    }

    @Override
    public double calculatePrice(Ticket t, Instant exitTime) {
        long minutes = Duration.between(t.getEntryTime(), exitTime).toMinutes();
        long hours = Math.max(1, (minutes + 59) / 60);   // ceil(minutes/60), integer, min 1 hour
        return hours * hourlyRate;
    }
}
