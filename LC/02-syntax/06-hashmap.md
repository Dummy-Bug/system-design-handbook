# 06 — HashMap

## Declaration

```java
Map<Character, Integer> mp = new HashMap<>();
Map<String, List<Integer[]>> mp = new HashMap<>();  // complex — read inside out
```

## Core Operations

```java
Map<Character, Integer> mp = new HashMap<>();

mp.put('a', 1);              // insert — mp = {'a':1}
mp.put('a', 5);              // overwrites — mp = {'a':5}
mp.get('a');                 // 5 — returns null if key doesn't exist (not error!)
mp.getOrDefault('a', 0);     // 5 — returns 0 if key missing, safe version of get
mp.containsKey('a');         // true
mp.containsValue(5);         // true — O(n), rarely used
mp.remove('a');              // removes key 'a'
mp.remove('a', 5);           // removes only if key='a' maps to value=5
mp.size();                   // number of entries
mp.isEmpty();                // true if empty
mp.replace('a', 99);         // update value only if key exists
```

## Frequency Pattern (most common in LC)

```java
// verbose but clear
mp.put(c, mp.getOrDefault(c, 0) + 1);

// shorthand — avoid in contests if syntax is shaky
// mp.merge(c, 1, Integer::sum);
```

## putIfAbsent

```java
mp.putIfAbsent('a', 0);   // puts 0 only if 'a' not already in map
                           // does NOT overwrite existing value
```

## computeIfAbsent — for grouping patterns

```java
// without computeIfAbsent — verbose
if (!mp.containsKey(key)) {
    mp.put(key, new ArrayList<>());
}
mp.get(key).add("eat");

// with computeIfAbsent — one line
mp.computeIfAbsent(key, k -> new ArrayList<>()).add("eat");
// "get list for key, create empty ArrayList if missing, then add"
```

**Classic use case — group anagrams:**
```java
Map<String, List<String>> mp = new HashMap<>();
for (String word : words) {
    char[] arr = word.toCharArray();
    Arrays.sort(arr);
    String key = new String(arr);                              // "eat" → "aet"
    mp.computeIfAbsent(key, k -> new ArrayList<>()).add(word); // group by sorted key
}
```

## Iteration

```java
// entries (key + value) — use this most often
for (Map.Entry<Character, Integer> entry : mp.entrySet()) {
    char key = entry.getKey();    // getKey() — needs ()
    int val = entry.getValue();   // getValue() — needs ()
}

// keys only
for (char key : mp.keySet()) { }

// values only
for (int val : mp.values()) { }
```

## Gotchas

- `mp.get(key)` returns `null` if key missing — always use `getOrDefault` to avoid NPE
- `entrySet()` not `entryset()` — case sensitive
- `getKey()` and `getValue()` need `()` — they are methods not properties
- `containsValue` is O(n) — never use it in a hot loop
- `putIfAbsent` does NOT overwrite — `put` always overwrites
