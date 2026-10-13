package services;


import models.*;
import strategies.pricing.PricingStrategy;

import java.time.LocalDateTime;
import java.util.*;

public class BookMyShowService {

    private final List<Show> shows = new ArrayList<>();
    private final List<Theatre> theatres = new ArrayList<>();
    private final List<PricingStrategy> pricingStrategies = new ArrayList<>();

    private static final BookMyShowService instance = new BookMyShowService();

    private BookMyShowService() {
    }

    public static BookMyShowService getInstance() {
        return instance;
    }

    public void addTheatres(Theatre theatre) {
        theatres.add(theatre);
    }

    public void addShow(Show show) {
        shows.add(show);
    }

    public void addPricingStrategy(PricingStrategy pricingStrategy) {
        pricingStrategies.add(pricingStrategy);
    }

    private EnumMap<SeatType, Double> priceFor(Show show) {
        EnumMap<SeatType, Double> prices = new EnumMap<>(show.getPrices());
        for (PricingStrategy pricingStrategy : pricingStrategies) {
            prices = pricingStrategy.apply(show, prices);
        }
        return prices;
    }

    public List<ShowSeat> getShowSeats(Show show) {
        if (!show.isOpenForBooking()) {
            throw new RuntimeException("Show has already started");
        }
        return show.getShowSeats();
    }

    public List<City> getAllCities() {
        Set<City> cities = new HashSet<>();
        for (Theatre theatre : theatres) {
            cities.add(theatre.getCity());
        }
        return new ArrayList<>(cities);
    }

    public List<Movie> getAllMovies(City city) {
        Set<Movie> movies = new HashSet<>();
        for (Show show : shows) {
            if (show.getScreen().getTheatre().getCity().equals(city)) {
                movies.add(show.getMovie());
            }
        }
        return new ArrayList<>(movies);
    }

    public List<Show> getAllShowsOfMovie(City city, Movie movie) {
        Set<Show> uniqueShows = new HashSet<>();
        for (Show show : shows) {
            if (show.getScreen().getTheatre().getCity().equals(city)
                    && show.getMovie().equals(movie)
                    && show.isOpenForBooking()) {
                uniqueShows.add(show);
            }
        }
        return new ArrayList<>(uniqueShows);
    }


    public synchronized Optional<Booking> lockShowSeats(Show show, List<String> seatLabels, User user) {

        if (!show.isOpenForBooking()) {
            return Optional.empty();
        }

        if (seatLabels.isEmpty()) {
            return Optional.empty();
        }

        List<ShowSeat> showSeats = new ArrayList<>();
        for (String label : seatLabels) {
            Optional<ShowSeat> showSeat = show.getShowSeat(label);
            if (showSeat.isEmpty()) {
                return Optional.empty();
            }
            if (!showSeats.contains(showSeat.get())) {
                showSeats.add(showSeat.get());
            }
        }

        for (ShowSeat showSeat : showSeats) {
            if (!showSeat.getStatus().equals(ShowSeatStatus.FREE)) {
                return Optional.empty();
            }
        }

        Booking booking = new Booking(java.util.UUID.randomUUID().toString(), show, showSeats, user, priceFor(show));


        for (ShowSeat showSeat : showSeats) {
            showSeat.setLockedBy(booking);
        }
        return Optional.of(booking);

    }

    public synchronized Optional<Booking> confirmBooking(Booking booking, double amount) {

        if (!booking.getStatus().equals(BookingStatus.PENDING)) {
            return Optional.empty();
        }

        if (booking.getExpiresAt().isBefore(LocalDateTime.now())) {
            booking.setStatus(BookingStatus.EXPIRED);
            return Optional.empty();
        }

        Show show = booking.getShow();

        if (!show.isOpenForBooking()) {
            return Optional.empty();
        }

        if (amount != booking.getAmount()) {
            booking.setStatus(BookingStatus.PAYMENT_FAILED);
            return Optional.empty();
        }

        booking.setStatus(BookingStatus.CONFIRMED);
        return Optional.of(booking);
    }

    public synchronized Optional<Booking> cancelBooking(Booking booking) {

        if (!booking.getStatus().equals(BookingStatus.CONFIRMED)) {
            return Optional.empty();
        }

        booking.setStatus(BookingStatus.CANCELLED);
        return Optional.of(booking);
    }
}
