package models;


public class Seat {
    private final String row;
    private final int col;

    private final SeatType type;

    public Seat(String row, int col, SeatType type) {
        this.row = row;
        this.col = col;
        this.type = type;
    }

    public String getSeatLabel() {
        return row + col;
    }

    public SeatType getSeatType() {
        return type;
    }
}
