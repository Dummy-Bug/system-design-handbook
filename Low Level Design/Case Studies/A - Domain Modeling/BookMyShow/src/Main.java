import models.*;
import services.BookMyShowService;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Optional;

public class Main {
    public static void main(String[] args) {

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

        EnumMap<SeatType, Double> prices1 = new EnumMap<>(SeatType.class);
        prices1.put(SeatType.SILVER, 50.0);
        prices1.put(SeatType.GOLD, 100.0);
        prices1.put(SeatType.PLATINUM, 200.0);
        Show show1 = new Show("s1", audi1, doomsday, now.plusHours(3), now.plusHours(5), prices1);

        EnumMap<SeatType, Double> prices2 = new EnumMap<>(SeatType.class);
        prices2.put(SeatType.SILVER, 150.0);
        prices2.put(SeatType.GOLD, 200.0);
        prices2.put(SeatType.PLATINUM, 300.0);
        Show show2 = new Show("s2", audi2, dune, now.plusHours(1), now.plusHours(2), prices2);

        service.addTheatres(nexus);
        service.addShow(show1);
        service.addShow(show2);

        User alpha = new User("Alpha", "alpha@gmail.com");
        User beta = new User("Beta", "beta@gmail.com");

        // --- FR3: cities, then movies in a city ---
        System.out.println("--- cities ---");
        for (City city : service.getAllCities()) {
            System.out.println(city.name());
        }

        System.out.println("\n--- movies in " + hsr.name() + " ---");
        for (Movie movie : service.getAllMovies(hsr)) {
            System.out.println(movie.name());
        }

        // --- FR4: upcoming shows of a movie ---
        System.out.println("\n--- shows of " + dune.name() + " in " + hsr.name() + " ---");
        for (Show show : service.getAllShowsOfMovie(hsr, dune)) {
            System.out.println(show.getId() + " | " + show.getScreen().getTheatre().getName() + " " + show.getScreen().getId()
                    + " | " + show.getStartTime() + " - " + show.getEndTime());
        }

        // --- FR5: seat map of a show ---
        System.out.println("\n--- seat map of " + show2.getId() + " ---");
        for (ShowSeat showSeat : service.getShowSeats(show2)) {
            System.out.println(showSeat.getShowSeatLabel() + " | " + showSeat.getSeat().getSeatType() + " | " + showSeat.getStatus());
        }

        Optional<Booking> bookingOptional = service.lockShowSeats(show2, show2.getShowSeats(), alpha);
        if (bookingOptional.isEmpty()) {
            throw new RuntimeException("Please select seats that are Free");
        }

        System.out.println("Please pay " + bookingOptional.get().getAmount() + " to confirm the Booking");

        Optional<Booking> confirmedBookingOptional = service.confirmBooking(bookingOptional.get(), bookingOptional.get().getAmount());
        if (confirmedBookingOptional.isEmpty()) {
            throw new RuntimeException("Payment failed");
        }
        Booking confirmedBooking = confirmedBookingOptional.get();

        System.out.println("Your Booking has been confirmed for Movie :- " + confirmedBooking.getShow().getMovie().name() +
                "show starts from " + confirmedBooking.getShow().getStartTime() + " Ends at " + confirmedBooking.getShow().getEndTime() +
                "Inside Theatre " + confirmedBooking.getShow().getScreen().getTheatre().getName());

    }
}
