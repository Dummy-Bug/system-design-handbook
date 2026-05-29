### #22 — Next Greater Node In Linked List
**Link:** https://leetcode.com/problems/next-greater-node-in-linked-list/
**Date attempted:** 2026-05-28 ~07:45
**Rating:** 1550–1600 band (Phase 1 acquisition — Monotonic stack blind spot)
**Time:** 37 min coding — first-submission AC ✓
**Pattern:** Monotonic stack (blind spot)

---

**Verbatim thinking:**

- "next greater" → monotonic stack
- linked list is forward-only, but "next greater" needs to look ahead — easier to process from the right
- reverse the linked list, then traverse: maintain a decreasing monotonic stack
- realized return type is an array, not a list — so no pointer juggling needed for output, just fill the array and reverse it at the end
- for each node: pop everything ≤ current val, top of stack (if any) is the next greater, else 0; then push current
- first LL problem in months — struggled with the reverse helper

**Insight:**
"Next greater element" is the canonical monotonic stack pattern. For a linked list (forward-only), reverse it first so you can process right-to-left. Maintain a strictly decreasing stack: pop all elements ≤ current (they can't be anyone's "next greater" now), the remaining top is the answer, then push current. Reverse the answer array at the end to restore original order.

**Key gotcha:**
Pop condition is `<=` not `<` — equal elements don't count as "greater", so they must be popped. Processing right-to-left (via reversal) is what makes the stack see "future" elements as already-processed.

**Complexity:**
O(n) time, O(n) space (stack + answer array).

**Solution code:**

```java
class Solution {

    private ListNode reverse(ListNode head){
        ListNode next = head.next;
        ListNode prev = null;

        while(true){
            head.next = prev;
            prev = head;
            head = next;
            if (head == null){
                return prev;
            }
            next = next.next;
        }
 
    }

    private int [] reverse(int[] nums){

        int n = nums.length;

        int i = 0;
        int j = n - 1;

        while( i < j){
            
            int temp = nums[i];
            nums[i] = nums[j];
            nums[j] = temp;

            i++;
            j--;
        } 
        
        return nums;
    }
    public int[] nextLargerNodes(ListNode head) {
        
        head = reverse(head);
        
        ListNode temp = head;
        int n = 0;

        while(temp != null){
            temp = temp.next;
            n++;
        }
        
        Deque<Integer> stack = new ArrayDeque<>();
        int [] ans = new int[n];


        temp = head;
        int i = 0;

        while(temp != null){

            int val = temp.val;

            while (!stack.isEmpty() && stack.peek() <= val){
                stack.pop();
            }

            if (!stack.isEmpty()){
                ans[i] = stack.peek();
            }
            else{
                ans[i] = 0;
            }
            stack.push(val);
            i++;
            temp = temp.next;
        }
        return reverse(ans);
    }
}
```
