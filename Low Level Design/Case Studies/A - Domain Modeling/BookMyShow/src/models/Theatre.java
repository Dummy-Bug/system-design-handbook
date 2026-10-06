package models;

import java.util.List;

public record Theatre(String id, String name, City city, List<Screen> screens) {
    public Theatre {
        screens = List.copyOf(screens);
    }
}
