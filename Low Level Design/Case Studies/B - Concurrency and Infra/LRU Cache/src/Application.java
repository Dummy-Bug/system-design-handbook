public class Application {

    public static void main(String[] args) {

        int size = 3;

        Cache<String, Integer> cache = new Cache<>(size);
        cache.put("a", 1);
        cache.put("b", 3);
        cache.put("c", 5);
        cache.put("a", 11);

        cache.put("d", 27);
        System.out.println(cache.get("b"));
        System.out.println(cache.get("a"));
        System.out.println(cache.get("c"));
        System.out.println(cache.get("d"));

        System.out.println("Fetching value of null key " + cache.get("z"));

    }
}
