package model;

public enum VehicleType {
    BIKE(SpotSize.SMALL),
    CAR(SpotSize.MEDIUM),
    TRUCK(SpotSize.LARGE);

    private final SpotSize minSize;

    VehicleType(SpotSize minSize) {
        this.minSize = minSize;
    }

    public SpotSize getMinSize() {
        return minSize;
    }
}
