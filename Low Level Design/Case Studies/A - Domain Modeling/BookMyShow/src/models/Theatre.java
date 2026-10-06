package models;

import java.util.List;

public record Theatre(String id, City city, List<Screen> screens) {
}
