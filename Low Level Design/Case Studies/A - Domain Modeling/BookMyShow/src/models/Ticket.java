package models;

import java.util.List;

public class Ticket {
    String id;
    Show show;
    List<ShowSeat> bookedSeats;
    User user;
    double amount;
}
