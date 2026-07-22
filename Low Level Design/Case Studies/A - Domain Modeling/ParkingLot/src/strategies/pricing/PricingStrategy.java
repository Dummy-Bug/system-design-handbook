package strategies.pricing;

import model.Ticket;

import java.time.Instant;

public interface PricingStrategy {

    public double calculatePrice(Ticket t, Instant exitTime);
}
