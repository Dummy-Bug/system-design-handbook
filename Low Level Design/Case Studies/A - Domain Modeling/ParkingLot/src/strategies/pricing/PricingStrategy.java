package strategies.pricing;

import model.Ticket;

import java.time.Instant;

public interface PricingStrategy {

    double calculatePrice(Ticket t, Instant exitTime);
}
