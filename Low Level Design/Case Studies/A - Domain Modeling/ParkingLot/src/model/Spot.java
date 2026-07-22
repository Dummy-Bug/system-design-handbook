package model;

public class Spot {

    private final String id;
    private final SpotSize size;
    private SpotStatus status;

    public synchronized boolean tryOccupy() {
        if (status == SpotStatus.FREE) {
            status = SpotStatus.OCCUPIED;
            return true;
        }
        return false;
    }

    public synchronized void release() {
        status = SpotStatus.FREE;
    }

    public Spot(String id, SpotSize size) {
        this.id = id;
        this.size = size;
        this.status = SpotStatus.FREE;
    }

    public String getId() {
        return id;
    }

    public SpotSize getSize() {
        return size;
    }

    public SpotStatus getStatus() {
        return status;
    }
}
