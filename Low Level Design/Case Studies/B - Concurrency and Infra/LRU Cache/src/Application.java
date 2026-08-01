public class Application {

    public static void main(String[] args) {

        int size = 3;

        Cache<String, Integer> cache = new Cache<>(size);
        cache.put("a", 1);
        cache.put("b", 3);
        cache.put("c", 5);
        cache.displayCache();
        cache.put("a", 11);
        cache.displayCache();

        cache.put("d", 27);
        cache.displayCache();
        System.out.println(cache.get("b"));
//        System.out.println(cache.get("a"));
//        System.out.println(cache.get("c"));
//        System.out.println(cache.get("d"));
//
//        System.out.println("Value of Key b is --> " + cache.get("b"));

    }
}
