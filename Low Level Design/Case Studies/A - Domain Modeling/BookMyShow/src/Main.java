import models.*;
import services.BookMyShowService;
import strategies.pricing.MorningDiscountPricing;
import strategies.pricing.WeekendSurgePricing;

import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Optional;

public class Main {
    public static void main(String[] args) throws InterruptedException {

        BookMyShowService service = BookMyShowService.getInstance();

        // --- admin setup ---
        City hsr = new City("HSR");

        List<Seat> seats = new ArrayList<>();
        seats.add(new Seat("A", 5, SeatType.SILVER));
        seats.add(new Seat("B", 5, SeatType.GOLD));
        seats.add(new Seat("C", 5, SeatType.PLATINUM));

        Theatre nexus = new Theatre("t1", "Nexus Mall", hsr);
        Screen audi1 = nexus.addScreen("audi-1", seats);
        Screen audi2 = nexus.addScreen("audi-2", seats);

        Movie doomsday = new Movie("m1", "DoomsDay");
        Movie dune = new Movie("m2", "Dune");

        LocalDateTime now = LocalDateTime.now();
        LocalDateTime nextMonday6pm = now.toLocalDate().with(TemporalAdjusters.next(DayOfWeek.MONDAY)).atTime(18, 0);

        EnumMap<SeatType, Double> prices1 = new EnumMap<>(SeatType.class);
        prices1.put(SeatType.SILVER, 50.0);
        prices1.put(SeatType.GOLD, 100.0);
        prices1.put(SeatType.PLATINUM, 200.0);
        Show show1 = new Show("s1", audi1, doomsday, nextMonday6pm.plusHours(3), nextMonday6pm.plusHours(5), prices1);

        EnumMap<SeatType, Double> prices2 = new EnumMap<>(SeatType.class);
        prices2.put(SeatType.SILVER, 150.0);
        prices2.put(SeatType.GOLD, 200.0);
        prices2.put(SeatType.PLATINUM, 300.0);
        Show show2 = new Show("s2", audi2, dune, nextMonday6pm, nextMonday6pm.plusHours(1), prices2);

        service.addTheatres(nexus);
        service.addShow(show1);
        service.addShow(show2);

        service.addPricingStrategy(new WeekendSurgePricing(20));
        service.addPricingStrategy(new MorningDiscountPricing(10));

        User alpha = new User("Alpha", "alpha@gmail.com");
        User beta = new User("Beta", "beta@gmail.com");

        // --- FR2: a second show on audi-2 that overlaps s2 is refused ---
        System.out.println("--- add an overlapping show on audi-2 ---");
        Show clash = new Show("s-clash", audi2, doomsday, nextMonday6pm.plusMinutes(30), nextMonday6pm.plusMinutes(150), prices2);
        System.out.println(service.addShow(clash) ? "added" : "rejected: audi-2 is busy then");

        // --- FR3: cities, then movies in a city ---
        System.out.println("\n--- cities ---");
        for (City city : service.getAllCities()) {
            System.out.println(city.name());
        }

        System.out.println("\n--- movies in " + hsr.name() + " ---");
        for (Movie movie : service.getAllMovies(hsr)) {
            System.out.println(movie.name());
        }

        // --- FR4: upcoming shows of a movie, and of a theatre ---
        System.out.println("\n--- shows of " + dune.name() + " in " + hsr.name() + " ---");
        for (Show show : service.getAllShowsOfMovie(hsr, dune)) {
            printShow(show);
        }

        System.out.println("\n--- shows at " + nexus.getName() + " ---");
        for (Show show : service.getAllShowsInTheatre(nexus)) {
            printShow(show);
        }

        // --- FR5: seat map of a show ---
        System.out.println("\n--- seat map of " + show2.getId() + " ---");
        printSeatMap(service, show2);

        // --- FR6: Alpha holds A5 and B5 ---
        System.out.println("\n--- Alpha holds A5, B5 ---");
        Optional<Booking> bookingOptional = service.lockShowSeats(show2, List.of("A5", "B5"), alpha);
        if (bookingOptional.isEmpty()) {
            throw new RuntimeException("Please select seats that are Free");
        }
        Booking alphaBooking = bookingOptional.get();
        System.out.println("held, please pay " + alphaBooking.getAmount() + " before " + alphaBooking.getExpiresAt());

        // --- FR6: Beta wants B5 and C5; B5 is held, so nothing is held, not even C5 ---
        System.out.println("\n--- Beta tries B5, C5 ---");
        System.out.println(service.lockShowSeats(show2, List.of("B5", "C5"), beta).isPresent() ? "held" : "rejected: a seat is taken");
        printSeatMap(service, show2);

        // --- FR8, FR9: Alpha pays and gets a ticket ---
        System.out.println("\n--- Alpha pays ---");
        Optional<Booking> confirmedBookingOptional = service.confirmBooking(alphaBooking, alphaBooking.getAmount());
        if (confirmedBookingOptional.isEmpty()) {
            throw new RuntimeException("Payment failed");
        }
        printTicket(confirmedBookingOptional.get());
        System.out.println("pay again: " + (service.confirmBooking(alphaBooking, alphaBooking.getAmount()).isPresent() ? "charged twice" : "rejected"));

        // --- FR8: a failed payment frees the seat at once ---
        System.out.println("\n--- Beta holds C5, payment fails ---");
        Booking betaBooking = service.lockShowSeats(show2, List.of("C5"), beta).get();
        System.out.println("pay 1.0 instead of " + betaBooking.getAmount() + ": "
                + (service.confirmBooking(betaBooking, 1.0).isPresent() ? "confirmed" : "rejected") + ", booking " + betaBooking.getStatus());
        printSeatMap(service, show2);

        // --- FR7, FR8: a hold that runs out cannot be paid ---
        System.out.println("\n--- hold on a show whose booking closes in 2 seconds, paid 3 seconds later ---");
        Show soon = new Show("s-soon", audi1, dune, now.plusMinutes(5).plusSeconds(2), now.plusMinutes(65), prices2);
        Booking lateBooking = service.lockShowSeats(soon, List.of("A5"), alpha).get();
        System.out.println("hold expires at " + lateBooking.getExpiresAt().toLocalTime());
        Thread.sleep(3_000);
        System.out.println("pay: " + (service.confirmBooking(lateBooking, lateBooking.getAmount()).isPresent() ? "confirmed" : "rejected")
                + ", booking " + lateBooking.getStatus() + ", A5 " + soon.getShowSeat("A5").get().getStatus());

        // --- FR11: Alpha cancels ---
        System.out.println("\n--- Alpha cancels ---");
        System.out.println(service.cancelBooking(alphaBooking).isPresent() ? "cancelled" : "could not cancel");
        printSeatMap(service, show2);

        // --- NFR1: two users go for A5 of s1 at the same moment ---
        System.out.println("\n--- Alpha and Beta grab A5 of " + show1.getId() + " at once ---");
        List<String> results = Collections.synchronizedList(new ArrayList<>());
        Thread alphaThread = new Thread(() -> results.add("Alpha: " + (service.lockShowSeats(show1, List.of("A5"), alpha).isPresent() ? "got it" : "rejected")));
        Thread betaThread = new Thread(() -> results.add("Beta: " + (service.lockShowSeats(show1, List.of("A5"), beta).isPresent() ? "got it" : "rejected")));
        alphaThread.start();
        betaThread.start();
        alphaThread.join();
        betaThread.join();
        results.forEach(System.out::println);

        // --- extension: pricing rules ---
        System.out.println("\n--- pricing: Gold seat B5, listed at 200 ---");
        LocalDateTime nextSaturday10am = now.toLocalDate().with(TemporalAdjusters.next(DayOfWeek.SATURDAY)).atTime(10, 0);
        Show mondayEvening = new Show("s3", audi1, dune, nextMonday6pm, nextMonday6pm.plusHours(2), prices2);
        Show saturdayMorning = new Show("s4", audi2, dune, nextSaturday10am, nextSaturday10am.plusHours(2), prices2);
        System.out.println("Monday 6 pm:    " + service.lockShowSeats(mondayEvening, List.of("B5"), beta).get().getAmount());
        System.out.println("Saturday 10 am: " + service.lockShowSeats(saturdayMorning, List.of("B5"), beta).get().getAmount());
    }

    private static void printShow(Show show) {
        System.out.println(show.getId() + " | " + show.getMovie().name() + " | " + show.getScreen().getTheatre().getName() + " " + show.getScreen().getId()
                + " | " + show.getStartTime() + " - " + show.getEndTime());
    }

    private static void printSeatMap(BookMyShowService service, Show show) {
        for (ShowSeat showSeat : service.getShowSeats(show)) {
            System.out.println("  " + showSeat.getShowSeatLabel() + " | " + showSeat.getSeat().getSeatType() + " | " + showSeat.getStatus());
        }
    }

    private static void printTicket(Booking booking) {
        Show show = booking.getShow();
        System.out.println("ticket " + booking.getId());
        System.out.println("  " + show.getMovie().name() + " | " + show.getScreen().getTheatre().getName() + " " + show.getScreen().getId() + " | " + show.getStartTime());
        for (ShowSeat showSeat : booking.getShowSeats()) {
            System.out.println("  seat " + showSeat.getShowSeatLabel() + " (" + showSeat.getSeat().getSeatType() + ")");
        }
        System.out.println("  total " + booking.getAmount());
    }
}
