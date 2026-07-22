package strategies.payment;

public class CashPaymentStrategy implements PaymentStrategy {

    @Override
    public boolean pay(double amount) {
        System.out.println("Payment SUCCESS");
        return true;
    }
}
