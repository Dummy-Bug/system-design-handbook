package services;


import models.*;

import java.time.LocalDateTime;
import java.util.*;

public class BookMyShowService {

    private final List<Show> shows = new ArrayList<>();
    private final List<Theatre> theatres = new ArrayList<>();

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

    public List<ShowSeat> getShowSeats(Show show) {
        if (!show.isOpenForBooking()) {
            throw new RuntimeException("Show has already started");
        }
        List<ShowSeat> showSeats = show.getShowSeats();

        for (ShowSeat showSeat : showSeats) {

            if (showSeat.getStatus().equals(ShowSeatStatus.LOCKED)) {
                Booking booking = showSeat.getLockedBy();

                if (booking.getExpiresAt().isBefore(LocalDateTime.now())) {
                    releaseHold(booking);
                }
            } else if (showSeat.getStatus().equals(ShowSeatStatus.BOOKED)) {
                if (show.getEndTime().isBefore(LocalDateTime.now())) {
                    releaseHold(showSeat.getLockedBy());
                }
            }
        }
        return new ArrayList<>(showSeats);
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


    public synchronized Optional<Booking> lockShowSeats(Show show, List<ShowSeat> showSeats, User user) {

        if (!show.isOpenForBooking()) {
            throw new RuntimeException("Show has already started");
        }

        for (ShowSeat showSeat : showSeats) {

            Booking booking = showSeat.getLockedBy();
            if (booking == null) continue;

            else if (booking.getStatus().equals(BookingStatus.PENDING) &&
                    booking.getExpiresAt().isAfter(LocalDateTime.now())) {
                return Optional.empty();

            } else if (booking.getStatus().equals(BookingStatus.CONFIRMED)) {
                if (show.getEndTime().isBefore(LocalDateTime.now())) {
                    releaseHold(booking);
                } else return Optional.empty();
            }

        }

        Booking booking = new Booking(java.util.UUID.randomUUID().toString(), show, showSeats, user);


        for (ShowSeat showSeat : showSeats) {
            showSeat.setStatus(ShowSeatStatus.LOCKED);
            showSeat.setLockedBy(booking);
        }
        return Optional.of(booking);

    }

    public synchronized Optional<Booking> confirmBooking(Booking booking, double amount) {

        if (booking.getStatus().equals(BookingStatus.CONFIRMED) || booking.getStatus().equals(BookingStatus.CANCELLED)) {
            return Optional.empty();
        }

        if (booking.getExpiresAt().isBefore(LocalDateTime.now())) {
            return Optional.empty();
        }

        Show show = booking.getShow();

        if (!show.isOpenForBooking()) {
            releaseHold(booking);
            throw new RuntimeException("Show has already started");
        }

        if (amount != booking.getAmount()) {
            return Optional.empty();
        }

        List<ShowSeat> showSeats = booking.getShowSeats();
        for (ShowSeat showSeat : showSeats) {
            showSeat.setStatus(ShowSeatStatus.BOOKED);
        }
        booking.setStatus(BookingStatus.CONFIRMED);
        return Optional.of(booking);
    }

    public Optional<Booking> cancelBooking(Booking booking) {

        if (booking.getStatus().equals(BookingStatus.CONFIRMED)) {
            releaseHold(booking);
            booking.setStatus(BookingStatus.CANCELLED);
        }
        return Optional.of(booking);
    }

    public synchronized void releaseHold(Booking booking) {

        List<ShowSeat> showSeats = booking.getShowSeats();

        for (ShowSeat showSeat : showSeats) {
            showSeat.setStatus(ShowSeatStatus.FREE);
            showSeat.setLockedBy(null);
        }
    }
}
