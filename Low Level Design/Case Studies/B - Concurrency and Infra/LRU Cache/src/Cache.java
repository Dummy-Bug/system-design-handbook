import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

public class Cache<K, V> {

    private class Node {

        K key;
        V value;

        Node prev;
        Node next;

        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<K, Node> map = new HashMap<>();

    private final Node head = new Node(null, null);
    private final Node tail = new Node(null, null);

    public Cache(int size) {
        this.capacity = size;
        head.next = tail;
        tail.prev = head;
    }

    private void updateOrdering(K key) {
        Node node = map.get(key);
        if (head.next == node) {
            return;
        } else if (tail.prev == node) {
            head.next.prev = node;
            node.next = head.next;

            tail.prev = node.prev;
            node.prev = null;

        } else {
            node.prev.next = node.next;
            node.next.prev = node.prev;

            head.next.prev = node;
            node.next = head.next;
            node.prev = null;

        }

    }

    public V get(K key) {
        if (!map.containsKey(key)) return null;
        updateOrdering(key);
        return map.get(key).value;
    }

    private void initializeMap(K key, V value) {
        Node node = new Node(value);
        head = node;
        tail = node;
        map.put(key, node);
    }

    public void put(K key, V value) {
        if (map.isEmpty()) {
            initializeMap(key, value);
            return;
        }
        if (map.containsKey(key)) {
            updateOrdering(key);
            Node node = map.get(key);
            node.value = value;
        } else {

        }
    }

    private Node<V> findNodeToEvict() {
        return tail;
    }


}
