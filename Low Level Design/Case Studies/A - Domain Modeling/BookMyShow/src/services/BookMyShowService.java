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
                    && show.getStartTime().isAfter(LocalDateTime.now().plusMinutes(5L))) {
                uniqueShows.add(show);
            }
        }
        return new ArrayList<>(uniqueShows);
    }
}
