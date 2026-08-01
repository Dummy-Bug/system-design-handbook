import java.util.HashMap;
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

    private final int CAPACITY;
    private final Map<K, Node> map = new HashMap<>();

    private final Node head = new Node(null, null);
    private final Node tail = new Node(null, null);

    public Cache(int size) {
        CAPACITY = size;
        head.next = tail;
        tail.prev = head;
    }

    private void addToFront(Node node) {

        node.prev = head;
        node.next = head.next;

        head.next.prev = node;
        head.next = node;

    }


    public V get(K key) {
        if (!map.containsKey(key)) return null;
        Node node = map.get(key);
        removeNode(node);
        addToFront(node);
        return node.value;
    }

    private void removeLRU() {
        if (tail.prev == head) return;
        Node node = tail.prev;
        map.remove(node.key);
        removeNode(node);
    }
    private void removeNode(Node node) {
        if (tail.prev == node) {
            tail.prev = node.prev;
        }
        node.prev.next = node.next;
        node.next.prev = node.prev;

    }

    public void put(K key, V value) {

        if (map.containsKey(key)) {
            Node node = map.get(key);
            node.value = value;
            removeNode(node);
            addToFront(node);
            return;
        }
        Node node = new Node(key, value);
        if (map.size() == CAPACITY) {
            System.out.println("Cache FULL size == " + map.size() + " Inserting Key :: " + key);
            removeLRU();
        }
        addToFront(node);
        map.put(key, node);
    }

    public void displayCache() {
        System.out.println("Cache size == " + map.size());
        Node temp = head.next;

        while (temp != tail) {
            System.out.print("\t" + temp.key + " - " + temp.value + "\n");
            temp = temp.next;
        }

    }


}
