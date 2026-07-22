package model;

public class Spot {

    private final String id;
    private final SpotSize size;
    private SpotStatus status;

    public void setStatus(SpotStatus status) {
        this.status = status;
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
