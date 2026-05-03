from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
QUESTION_DATA_DIR = ROOT / 'data' / 'question_data'


def qa(question, answer):
    return {'q': question, 'a': answer}


def approach(name, badge, badge_color, description, time, space, why_not, code):
    return {
        'name': name,
        'badge': badge,
        'badge_color': badge_color,
        'description': description,
        'time': time,
        'space': space,
        'why_not': why_not,
        'code': code,
    }


def write_problem(topic_slug, filename, data):
    path = QUESTION_DATA_DIR / topic_slug / filename
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


TOPIC_PROBLEMS = {
    'arrays-hashing': [
        {
            'id': 1,
            'leetcode_number': 1,
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'url': 'https://leetcode.com/problems/two-sum/',
            'problem_statement': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Assume exactly one solution and do not use the same element twice.',
            'examples': [
                {'input': 'nums = [2,7,11,15], target = 9', 'output': '[0,1]', 'explanation': 'nums[0] and nums[1] sum to 9.'},
                {'input': 'nums = [3,2,4], target = 6', 'output': '[1,2]', 'explanation': '2 and 4 add to 6.'},
            ],
            'constraints': ['2 ≤ nums.length ≤ 10⁴', '-10⁹ ≤ nums[i], target ≤ 10⁹', 'Exactly one solution exists.'],
            'intuition': 'Keep a map from number to index. For each element, check if its complement target - num already exists in the map.',
            'approaches': [
                approach(
                    'HashMap One Pass',
                    'Optimal',
                    'green',
                    'Traverse once and store each number with its index. When a complement appears, return the pair.',
                    'O(n)',
                    'O(n)',
                    None,
                    """class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[]{map.get(complement), i};
            }
            map.put(nums[i], i);
        }
        return new int[]{};
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why use a HashMap instead of sorting?', 'Sorting costs O(n log n) and loses original indices. The HashMap method is O(n) and preserves positions.'),
                qa('How are duplicates handled?', 'If a duplicate is needed, the earlier occurrence is already stored in the map so the second occurrence can form the pair.'),
            ],
        },
        {
            'id': 2,
            'leetcode_number': 49,
            'title': 'Group Anagrams',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/group-anagrams/',
            'problem_statement': 'Given an array of strings strs, group the anagrams together. Return the answer in any order.',
            'examples': [
                {'input': 'strs = ["eat","tea","tan","ate","nat","bat"]', 'output': '[["bat"],["nat","tan"],["ate","eat","tea"]]', 'explanation': 'Strings that are anagrams appear in the same group.'},
                {'input': 'strs = [""]', 'output': '[[""]]', 'explanation': 'The empty string is grouped with itself.'},
            ],
            'constraints': ['1 ≤ strs.length ≤ 10⁴', '0 ≤ strs[i].length ≤ 100', 'strs[i] consists of lowercase English letters.'],
            'intuition': 'Anagrams share the same character counts. Use a canonical key to group strings that have the same letters.',
            'approaches': [
                approach(
                    'Frequency Count Key',
                    'Optimal',
                    'green',
                    'Use a 26-length frequency array for each string, convert it to a key, and group by that key.',
                    'O(n·k)',
                    'O(n·k)',
                    None,
                    """class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String s : strs) {
            int[] counts = new int[26];
            for (char c : s.toCharArray()) {
                counts[c - 'a']++;
            }
            String key = Arrays.toString(counts);
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }
        return new ArrayList<>(groups.values());
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why use character frequency instead of sorting each string?', 'Frequency counting is O(k) per string. Sorting is O(k log k) and slower for longer strings.'),
                qa('What if strings contain uppercase letters?', 'Extend the key generation to include uppercase ranges or use a larger frequency array to cover the full alphabet.'),
            ],
        },
        {
            'id': 3,
            'leetcode_number': 217,
            'title': 'Contains Duplicate',
            'difficulty': 'Easy',
            'url': 'https://leetcode.com/problems/contains-duplicate/',
            'problem_statement': 'Given an integer array nums, return true if any value appears at least twice in the array, and false if every element is distinct.',
            'examples': [
                {'input': 'nums = [1,2,3,1]', 'output': 'true', 'explanation': 'The value 1 appears more than once.'},
                {'input': 'nums = [1,2,3,4]', 'output': 'false', 'explanation': 'All values are unique.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10⁵', '-10⁹ ≤ nums[i] ≤ 10⁹'],
            'intuition': 'Use a set to remember values already seen. If a value is added twice, it is a duplicate.',
            'approaches': [
                approach(
                    'HashSet Lookup',
                    'Optimal',
                    'green',
                    'Add each number to a set while scanning. If a number already exists, return true.',
                    'O(n)',
                    'O(n)',
                    None,
                    """class Solution {
    public boolean containsDuplicate(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        for (int num : nums) {
            if (!seen.add(num)) {
                return true;
            }
        }
        return false;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why is HashSet a good choice here?', 'HashSet membership checks are average O(1), so duplicates are detected quickly.'),
                qa('What if the array must not use extra space?', 'Sort the array and then check adjacent values. This uses O(1) extra space but O(n log n) time.'),
            ],
        },
        {
            'id': 4,
            'leetcode_number': 238,
            'title': 'Product of Array Except Self',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/product-of-array-except-self/',
            'problem_statement': 'Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i]. Solve it without using division and in O(n) time.',
            'examples': [
                {'input': 'nums = [1,2,3,4]', 'output': '[24,12,8,6]', 'explanation': 'Each answer position multiplies all values except the current one.'},
                {'input': 'nums = [-1,1,0,-3,3]', 'output': '[0,0,9,0,0]', 'explanation': 'Zero resets products for all positions except itself.'},
            ],
            'constraints': ['2 ≤ nums.length ≤ 10⁵', '-30 ≤ nums[i] ≤ 30', 'The product of any prefix or suffix fits in a 32-bit integer.'],
            'intuition': 'Compute prefix products and suffix products separately, then multiply them for each index.',
            'approaches': [
                approach(
                    'Prefix and Suffix Pass',
                    'Optimal',
                    'green',
                    'Build the answer using left products then multiply by a rolling right product in a second pass.',
                    'O(n)',
                    'O(1) extra',
                    None,
                    """class Solution {
    public int[] productExceptSelf(int[] nums) {
        int n = nums.length;
        int[] answer = new int[n];
        answer[0] = 1;
        for (int i = 1; i < n; i++) {
            answer[i] = answer[i - 1] * nums[i - 1];
        }
        int rightProduct = 1;
        for (int i = n - 1; i >= 0; i--) {
            answer[i] *= rightProduct;
            rightProduct *= nums[i];
        }
        return answer;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why can the output array be excluded from space complexity?', 'The output array is required by the problem, so extra auxiliary space ignores it in the usual analysis.'),
                qa('Why not use division?', 'Division breaks when the array contains zero and the problem explicitly forbids it.'),
            ],
        },
        {
            'id': 5,
            'leetcode_number': 53,
            'title': 'Maximum Subarray',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/maximum-subarray/',
            'problem_statement': 'Given an integer array nums, find the contiguous subarray with the largest sum and return its sum.',
            'examples': [
                {'input': 'nums = [-2,1,-3,4,-1,2,1,-5,4]', 'output': '6', 'explanation': 'The subarray [4,-1,2,1] has the maximum sum.'},
                {'input': 'nums = [1]', 'output': '1', 'explanation': 'Single element array returns that element.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10⁵', '-10⁴ ≤ nums[i] ≤ 10⁴'],
            'intuition': 'At each index, decide whether to extend the current subarray or start a new one. Track the maximum sum so far.',
            'approaches': [
                approach(
                    'Kadane’s Algorithm',
                    'Optimal',
                    'green',
                    'Maintain a running sum and reset it when it becomes negative, while recording the best sum seen.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int maxSubArray(int[] nums) {
        int currentSum = nums[0];
        int maxSum = nums[0];
        for (int i = 1; i < nums.length; i++) {
            currentSum = Math.max(nums[i], currentSum + nums[i]);
            maxSum = Math.max(maxSum, currentSum);
        }
        return maxSum;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why start with nums[0] instead of 0?', 'If all numbers are negative, starting from 0 would give an incorrect answer of 0 instead of the true maximum negative sum.'),
                qa('How can you recover the subarray itself?', 'Track the temporary start index when resetting currentSum, and update best start/end positions whenever maxSum improves.'),
            ],
        },
        {
            'id': 6,
            'leetcode_number': 152,
            'title': 'Maximum Product Subarray',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/maximum-product-subarray/',
            'problem_statement': 'Given an integer array nums, find the contiguous subarray within the array that has the largest product and return that product.',
            'examples': [
                {'input': 'nums = [2,3,-2,4]', 'output': '6', 'explanation': 'The subarray [2,3] has product 6.'},
                {'input': 'nums = [-2,0,-1]', 'output': '0', 'explanation': 'Zero resets the product; the best product is 0.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 2·10⁴', '-10 ≤ nums[i] ≤ 10'],
            'intuition': 'Track both the maximum and minimum products ending at each index because a negative number can swap them.',
            'approaches': [
                approach(
                    'Maintain Max and Min',
                    'Optimal',
                    'green',
                    'Update the current maximum and minimum products at each position and use them to compute the result.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int maxProduct(int[] nums) {
        int maxProd = nums[0];
        int minProd = nums[0];
        int result = nums[0];
        for (int i = 1; i < nums.length; i++) {
            int n = nums[i];
            if (n < 0) {
                int temp = maxProd;
                maxProd = minProd;
                minProd = temp;
            }
            maxProd = Math.max(n, maxProd * n);
            minProd = Math.min(n, minProd * n);
            result = Math.max(result, maxProd);
        }
        return result;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why keep both max and min products?', 'A negative number can turn the current minimum product into the maximum, so both must be tracked.'),
                qa('How does zero affect the scan?', 'Zero resets the running products, so the algorithm effectively starts a new subarray after any zero.'),
            ],
        },
        {
            'id': 7,
            'leetcode_number': 128,
            'title': 'Longest Consecutive Sequence',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/longest-consecutive-sequence/',
            'problem_statement': 'Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.',
            'examples': [
                {'input': 'nums = [100,4,200,1,3,2]', 'output': '4', 'explanation': 'The sequence [1,2,3,4] is the longest consecutive subsequence.'},
                {'input': 'nums = [0,3,7,2,5,8,4,6,0,1]', 'output': '9', 'explanation': 'The numbers 0 through 8 form a consecutive run.'},
            ],
            'constraints': ['0 ≤ nums.length ≤ 10⁵', '-10⁹ ≤ nums[i] ≤ 10⁹'],
            'intuition': 'Only start counting from numbers that do not have a predecessor. Use a set for fast membership tests.',
            'approaches': [
                approach(
                    'HashSet Scan',
                    'Optimal',
                    'green',
                    'Put all numbers into a set and expand each sequence from its smallest element.',
                    'O(n)',
                    'O(n)',
                    None,
                    """class Solution {
    public int longestConsecutive(int[] nums) {
        Set<Integer> set = new HashSet<>();
        for (int num : nums) {
            set.add(num);
        }
        int best = 0;
        for (int num : set) {
            if (!set.contains(num - 1)) {
                int current = num;
                int length = 1;
                while (set.contains(current + 1)) {
                    current++;
                    length++;
                }
                best = Math.max(best, length);
            }
        }
        return best;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why only start from sequence heads?', 'Starting from a number with a predecessor duplicates work. Heads ensure each sequence is counted once.'),
                qa('Is this O(n)?', 'Yes. Each element is processed a constant number of times, since sequences are only traversed from their starts.'),
            ],
        },
        {
            'id': 8,
            'leetcode_number': 287,
            'title': 'Find the Duplicate Number',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/find-the-duplicate-number/',
            'problem_statement': 'Given an array nums containing n + 1 integers where each integer is between 1 and n inclusive, return the duplicate number without modifying the array and using only constant extra space.',
            'examples': [
                {'input': 'nums = [1,3,4,2,2]', 'output': '2', 'explanation': '2 appears twice.'},
                {'input': 'nums = [3,1,3,4,2]', 'output': '3', 'explanation': '3 is the duplicate value.'},
            ],
            'constraints': ['2 ≤ n ≤ 10⁵', 'nums.length == n + 1', '1 ≤ nums[i] ≤ n'],
            'intuition': 'Treat the array as a linked list of indices. A duplicate creates a cycle, and cycle detection finds the repeated value.',
            'approaches': [
                approach(
                    'Floyd’s Cycle Detection',
                    'Optimal',
                    'green',
                    'Use tortoise and hare pointers on the implicit linked list defined by values → indices to locate the cycle start.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int findDuplicate(int[] nums) {
        int tortoise = nums[0];
        int hare = nums[0];
        do {
            tortoise = nums[tortoise];
            hare = nums[nums[hare]];
        } while (tortoise != hare);
        tortoise = nums[0];
        while (tortoise != hare) {
            tortoise = nums[tortoise];
            hare = nums[hare];
        }
        return hare;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why does this problem have a cycle?', 'The range 1..n and n+1 numbers force at least one value to repeat, which makes the implicit next-pointer graph cyclic.'),
                qa('What if you sort the array?', 'Sorting would find the duplicate but requires modifying the input and costs O(n log n). The cycle method is O(n) and space O(1).'),
            ],
        },
        {
            'id': 9,
            'leetcode_number': 268,
            'title': 'Missing Number',
            'difficulty': 'Easy',
            'url': 'https://leetcode.com/problems/missing-number/',
            'problem_statement': 'Given an array containing n distinct numbers in the range [0, n], return the only number missing from the array.',
            'examples': [
                {'input': 'nums = [3,0,1]', 'output': '2', 'explanation': '2 is the missing value.'},
                {'input': 'nums = [0,1]', 'output': '2', 'explanation': 'The missing value is n=2.'},
            ],
            'constraints': ['n == nums.length', '1 ≤ n ≤ 10⁴', '0 ≤ nums[i] ≤ n', 'All numbers are unique.'],
            'intuition': 'The numbers 0..n have a known sum. Subtracting the given numbers from that sum reveals the missing value. XOR also works.',
            'approaches': [
                approach(
                    'Sum Formula',
                    'Optimal',
                    'green',
                    'Compute n*(n+1)/2 and subtract the sum of the array.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        int expected = n * (n + 1) / 2;
        int actual = 0;
        for (int num : nums) {
            actual += num;
        }
        return expected - actual;
    }
}""",
                ),
                approach(
                    'XOR Trick',
                    'Optimal',
                    'green',
                    'XOR all numbers from 0..n and XOR with the array values. The missing number remains.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int missingNumber(int[] nums) {
        int missing = nums.length;
        for (int i = 0; i < nums.length; i++) {
            missing ^= i ^ nums[i];
        }
        return missing;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why does XOR find the missing number?', 'XORing every number twice cancels them out, leaving only the missing value.'),
                qa('Which method avoids overflow?', 'The XOR method avoids overflow, while the sum formula can overflow for very large n, though not within the problem constraints.'),
            ],
        },
        {
            'id': 10,
            'leetcode_number': 442,
            'title': 'Find All Duplicates in an Array',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/find-all-duplicates-in-an-array/',
            'problem_statement': 'Given an array of integers where 1 ≤ nums[i] ≤ n (n = size of array), some elements appear twice and others appear once. Return all elements that appear twice.',
            'examples': [
                {'input': 'nums = [4,3,2,7,8,2,3,1]', 'output': '[2,3]', 'explanation': '2 and 3 each appear twice.'},
                {'input': 'nums = [1,1,2]', 'output': '[1]', 'explanation': 'Only 1 appears twice.'},
            ],
            'constraints': ['n == nums.length', '1 ≤ n ≤ 10⁵', '1 ≤ nums[i] ≤ n', 'Each integer appears once or twice.'],
            'intuition': 'Index-marking works because values map to indices. Negate the value at the mapped index to mark it seen; if it is already negative, the number is a duplicate.',
            'approaches': [
                approach(
                    'Index Marking',
                    'Optimal',
                    'green',
                    'Use each value as an index and flip the sign of the visited position. A second visit indicates a duplicate.',
                    'O(n)',
                    'O(1)',
                    None,
                    """class Solution {
    public List<Integer> findDuplicates(int[] nums) {
        List<Integer> duplicates = new ArrayList<>();
        for (int num : nums) {
            int idx = Math.abs(num) - 1;
            if (nums[idx] < 0) {
                duplicates.add(Math.abs(num));
            } else {
                nums[idx] = -nums[idx];
            }
        }
        return duplicates;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Does this modify the input?', 'Yes, it negates numbers in place. If the original array must remain unchanged, use a HashMap instead.'),
                qa('Why is this safe for 1..n values?', 'The input guarantees values lie in the index range, so each value maps to a valid index.'),
            ],
        },
        {
            'id': 11,
            'leetcode_number': 560,
            'title': 'Subarray Sum Equals K',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/subarray-sum-equals-k/',
            'problem_statement': 'Given an integer array nums and an integer k, return the total number of continuous subarrays whose sum equals k.',
            'examples': [
                {'input': 'nums = [1,1,1], k = 2', 'output': '2', 'explanation': 'Two subarrays [1,1] sum to 2.'},
                {'input': 'nums = [1,2,3], k = 3', 'output': '2', 'explanation': 'Subarrays [1,2] and [3] match.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 2·10⁴', '-1000 ≤ nums[i] ≤ 1000', '-10⁷ ≤ k ≤ 10⁷'],
            'intuition': 'Use prefix sums and count how many previous prefix sums differ from the current sum by k.',
            'approaches': [
                approach(
                    'Prefix Sum Frequency Map',
                    'Optimal',
                    'green',
                    'Track how many times each prefix sum has occurred. For each current sum, add the count of previous sums equal to currentSum - k.',
                    'O(n)',
                    'O(n)',
                    None,
                    """class Solution {
    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> freq = new HashMap<>();
        freq.put(0, 1);
        int sum = 0;
        int count = 0;
        for (int num : nums) {
            sum += num;
            count += freq.getOrDefault(sum - k, 0);
            freq.put(sum, freq.getOrDefault(sum, 0) + 1);
        }
        return count;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why initialize freq[0] = 1?', 'That accounts for subarrays starting at index 0 whose sum equals k.'),
                qa('Does this method work with negative numbers?', 'Yes. It relies on prefix sums and works for both positive and negative values.'),
            ],
        },
        {
            'id': 12,
            'leetcode_number': 523,
            'title': 'Continuous Subarray Sum',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/continuous-subarray-sum/',
            'problem_statement': 'Given an integer array nums and an integer k, return true if the array has a continuous subarray of size at least two whose elements sum to a multiple of k.',
            'examples': [
                {'input': 'nums = [23,2,4,6,7], k = 6', 'output': 'true', 'explanation': 'The subarray [2,4] sums to 6.'},
                {'input': 'nums = [23,2,6,4,7], k = 13', 'output': 'false', 'explanation': 'No valid subarray exists.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10⁵', '0 ≤ nums[i] ≤ 10000', '0 ≤ k ≤ 2³¹ - 1'],
            'intuition': 'If two prefix sums have the same remainder mod k, the subarray between them sums to a multiple of k. Track remainders and earliest indices.',
            'approaches': [
                approach(
                    'Remainder Map',
                    'Optimal',
                    'green',
                    'Store the first index for each remainder of prefixSum % k. A repeated remainder with distance ≥ 2 signals a valid subarray.',
                    'O(n)',
                    'O(k)',
                    None,
                    """class Solution {
    public boolean checkSubarraySum(int[] nums, int k) {
        Map<Integer, Integer> seen = new HashMap<>();
        seen.put(0, -1);
        int sum = 0;
        for (int i = 0; i < nums.length; i++) {
            sum += nums[i];
            if (k != 0) sum %= k;
            if (seen.containsKey(sum)) {
                if (i - seen.get(sum) > 1) return true;
            } else {
                seen.put(sum, i);
            }
        }
        return false;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('What if k is zero?', 'When k is zero, check for consecutive zeros or a subarray with sum exactly zero instead of using modulo arithmetic.'),
                qa('Why store the earliest index for each remainder?', 'Earliest indices maximize the subarray length and allow detection of the smallest valid subarray of size two or more.'),
            ],
        },
    ],
    'backtracking': [
        {
            'id': 1,
            'leetcode_number': 39,
            'title': 'Combination Sum',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/combination-sum/',
            'problem_statement': 'Given a set of distinct candidates and a target number, return all unique combinations of candidates where the chosen numbers sum to target. You may reuse the same number multiple times.',
            'examples': [
                {'input': 'candidates = [2,3,6,7], target = 7', 'output': '[[2,2,3],[7]]', 'explanation': 'Two combinations sum to 7.'},
                {'input': 'candidates = [2,3,5], target = 8', 'output': '[[2,2,2,2],[2,3,3],[3,5]]', 'explanation': 'All combinations using unlimited repeats.'},
            ],
            'constraints': ['1 ≤ candidates.length ≤ 30', '1 ≤ candidates[i] ≤ 200', 'All candidates are distinct.'],
            'intuition': 'Use recursion to build combinations, allowing repeated picks and pruning when the running sum exceeds the target.',
            'approaches': [
                approach(
                    'DFS with Pruning',
                    'Optimal',
                    'green',
                    'Recursively choose or skip each candidate, reusing it as needed while keeping the combination sorted to avoid duplicates.',
                    'O(N^target/min(candidates)) in the worst case',
                    'O(target/min(candidates)) recursion stack',
                    None,
                    """class Solution {
    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(candidates);
        backtrack(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] candidates, int remain, int start, List<Integer> comb, List<List<Integer>> result) {
        if (remain == 0) {
            result.add(new ArrayList<>(comb));
            return;
        }
        for (int i = start; i < candidates.length; i++) {
            if (candidates[i] > remain) break;
            comb.add(candidates[i]);
            backtrack(candidates, remain - candidates[i], i, comb, result);
            comb.remove(comb.size() - 1);
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why do we reuse the same candidate index on the recursive call?', 'Reusing the same index allows unlimited instances of that candidate to be included in the combination.'),
                qa('How do we avoid duplicate combinations?', 'We keep the recursion order fixed by only exploring candidates from the current index onward.'),
            ],
        },
        {
            'id': 2,
            'leetcode_number': 40,
            'title': 'Combination Sum II',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/combination-sum-ii/',
            'problem_statement': 'Given a collection of candidate numbers with possible duplicates and a target, return unique combinations where the numbers sum to target. Each number may be used at most once.',
            'examples': [
                {'input': 'candidates = [10,1,2,7,6,1,5], target = 8', 'output': '[[1,1,6],[1,2,5],[1,7],[2,6]]', 'explanation': 'Find unique combinations using each candidate once.'},
                {'input': 'candidates = [2,5,2,1,2], target = 5', 'output': '[[1,2,2],[5]]', 'explanation': 'Duplicate candidates are handled gracefully.'},
            ],
            'constraints': ['1 ≤ candidates.length ≤ 100', '1 ≤ candidates[i] ≤ 50'],
            'intuition': 'Sort the candidates and use recursion, skipping over duplicates at the same depth to avoid repeated combinations.',
            'approaches': [
                approach(
                    'DFS with Duplicate Skipping',
                    'Optimal',
                    'green',
                    'Sort the input and backtrack while skipping duplicates that would start a new branch at the same level.',
                    'O(2^n)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(candidates);
        backtrack(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] candidates, int remain, int start, List<Integer> comb, List<List<Integer>> result) {
        if (remain == 0) {
            result.add(new ArrayList<>(comb));
            return;
        }
        for (int i = start; i < candidates.length; i++) {
            if (i > start && candidates[i] == candidates[i - 1]) continue;
            if (candidates[i] > remain) break;
            comb.add(candidates[i]);
            backtrack(candidates, remain - candidates[i], i + 1, comb, result);
            comb.remove(comb.size() - 1);
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why skip duplicates at the same recursive level?', 'Skipping duplicates prevents generating the same combination from different positions in the sorted list.'),
                qa('Why advance i + 1 instead of i?', 'Each candidate can only be used once, so the next recursion should start after the current index.'),
            ],
        },
        {
            'id': 3,
            'leetcode_number': 17,
            'title': 'Letter Combinations of a Phone Number',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/letter-combinations-of-a-phone-number/',
            'problem_statement': 'Given a string containing digits 2-9 inclusive, return all possible letter combinations that the number could represent using telephone keypad letters.',
            'examples': [
                {'input': 'digits = "23"', 'output': '["ad","ae","af","bd","be","bf","cd","ce","cf"]', 'explanation': 'Combine letters from digits 2 and 3.'},
                {'input': 'digits = ""', 'output': '[]', 'explanation': 'No digits means no combinations.'},
            ],
            'constraints': ['0 ≤ digits.length ≤ 4', 'digits[i] is in the range [2, 9].'],
            'intuition': 'Use backtracking to append one letter per digit and explore all combinations.',
            'approaches': [
                approach(
                    'Recursive Combination Build',
                    'Optimal',
                    'green',
                    'Map each digit to its letters, then backtrack across digits building each string character by character.',
                    'O(4^n · n)',
                    'O(n)',
                    None,
                    """class Solution {
    private static final String[] KEYS = {
        "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
    };

    public List<String> letterCombinations(String digits) {
        List<String> result = new ArrayList<>();
        if (digits.isEmpty()) return result;
        backtrack(digits, 0, new StringBuilder(), result);
        return result;
    }

    private void backtrack(String digits, int index, StringBuilder current, List<String> result) {
        if (index == digits.length()) {
            result.add(current.toString());
            return;
        }
        String letters = KEYS[digits.charAt(index) - '0'];
        for (char letter : letters.toCharArray()) {
            current.append(letter);
            backtrack(digits, index + 1, current, result);
            current.deleteCharAt(current.length() - 1);
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('What is the branching factor for each digit?', 'Each digit maps to 3 or 4 letters, so the total combinations grow exponentially with the number of digits.'),
                qa('Why use StringBuilder instead of string concatenation?', 'StringBuilder avoids creating a new string at every step and is more efficient for repeated append/remove operations.'),
            ],
        },
        {
            'id': 4,
            'leetcode_number': 51,
            'title': 'N-Queens',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/n-queens/',
            'problem_statement': 'Place n queens on an n×n chessboard so that no two queens attack each other. Return all distinct solutions in board string form.',
            'examples': [
                {'input': 'n = 4', 'output': '[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]', 'explanation': 'There are two valid arrangements for n=4.'},
                {'input': 'n = 1', 'output': '[["Q"]]', 'explanation': 'Single queen on a 1x1 board.'},
            ],
            'constraints': ['1 ≤ n ≤ 9'],
            'intuition': 'Place queens row by row and use sets to track occupied columns, diagonals, and anti-diagonals.',
            'approaches': [
                approach(
                    'Backtracking with Diagonals',
                    'Optimal',
                    'green',
                    'Use recursion to place one queen per row while checking columns and diagonals for conflicts.',
                    'O(n!)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        backtrack(n, 0, new int[n], new HashSet<>(), new HashSet<>(), new HashSet<>(), result);
        return result;
    }

    private void backtrack(int n, int row, int[] queens, Set<Integer> cols, Set<Integer> diags, Set<Integer> antiDiags, List<List<String>> result) {
        if (row == n) {
            result.add(buildBoard(queens, n));
            return;
        }
        for (int col = 0; col < n; col++) {
            int diag = row - col;
            int antiDiag = row + col;
            if (cols.contains(col) || diags.contains(diag) || antiDiags.contains(antiDiag)) continue;
            queens[row] = col;
            cols.add(col);
            diags.add(diag);
            antiDiags.add(antiDiag);
            backtrack(n, row + 1, queens, cols, diags, antiDiags, result);
            cols.remove(col);
            diags.remove(diag);
            antiDiags.remove(antiDiag);
        }
    }

    private List<String> buildBoard(int[] queens, int n) {
        List<String> board = new ArrayList<>();
        for (int row = 0; row < n; row++) {
            char[] line = new char[n];
            Arrays.fill(line, '.');
            line[queens[row]] = 'Q';
            board.add(new String(line));
        }
        return board;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why use diagonals as row-col and row+col?', 'Those values uniquely identify the two diagonal directions and allow quick conflict detection.'),
                qa('Why is the solution exponential?', 'The problem examines all safe queen placements, which grows factorially with board size.'),
            ],
        },
        {
            'id': 5,
            'leetcode_number': 131,
            'title': 'Palindrome Partitioning',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/palindrome-partitioning/',
            'problem_statement': 'Given a string s, partition s into substrings such that every substring is a palindrome. Return all possible palindrome partitionings.',
            'examples': [
                {'input': 's = "aab"', 'output': '[["a","a","b"],["aa","b"]]', 'explanation': 'Two palindrome partitions exist.'},
                {'input': 's = "a"', 'output': '[["a"]]', 'explanation': 'Single character is a palindrome.'},
            ],
            'constraints': ['1 ≤ s.length ≤ 16', 's consists of lowercase English letters.'],
            'intuition': 'Backtrack by expanding palindrome substrings from the start index and recurse on the remainder.',
            'approaches': [
                approach(
                    'DFS with Palindrome Check',
                    'Optimal',
                    'green',
                    'Use recursion to choose a palindrome prefix and partition the remainder.',
                    'O(n · 2^n)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<String>> partition(String s) {
        List<List<String>> result = new ArrayList<>();
        backtrack(s, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(String s, int start, List<String> current, List<List<String>> result) {
        if (start == s.length()) {
            result.add(new ArrayList<>(current));
            return;
        }
        for (int end = start + 1; end <= s.length(); end++) {
            String sub = s.substring(start, end);
            if (isPalindrome(sub)) {
                current.add(sub);
                backtrack(s, end, current, result);
                current.remove(current.size() - 1);
            }
        }
    }

    private boolean isPalindrome(String s) {
        int i = 0, j = s.length() - 1;
        while (i < j) {
            if (s.charAt(i++) != s.charAt(j--)) return false;
        }
        return true;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('How can palindrome tests be optimized?', 'Use DP or memoization to avoid repeating palindrome checks for the same substring.'),
                qa('Why are results stored as new ArrayList copies?', 'Each partition branch must preserve its own combination independently of later backtracking changes.'),
            ],
        },
        {
            'id': 6,
            'leetcode_number': 47,
            'title': 'Permutations II',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/permutations-ii/',
            'problem_statement': 'Given a collection of numbers that may contain duplicates, return all unique permutations.',
            'examples': [
                {'input': 'nums = [1,1,2]', 'output': '[[1,1,2],[1,2,1],[2,1,1]]', 'explanation': 'Unique permutations of the multiset.'},
                {'input': 'nums = [1,2,3]', 'output': '[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]', 'explanation': 'All permutations when elements are distinct.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 8'],
            'intuition': 'Sort the numbers and backtrack while skipping duplicates at the same position.',
            'approaches': [
                approach(
                    'Backtracking with Visited Set',
                    'Optimal',
                    'green',
                    'Use a boolean visited array and skip duplicate values when they would appear in the same position twice.',
                    'O(n!)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<Integer>> permuteUnique(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(nums);
        backtrack(nums, new boolean[nums.length], new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] nums, boolean[] used, List<Integer> current, List<List<Integer>> result) {
        if (current.size() == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) continue;
            used[i] = true;
            current.add(nums[i]);
            backtrack(nums, used, current, result);
            current.remove(current.size() - 1);
            used[i] = false;
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why skip when nums[i]==nums[i-1] and !used[i-1]?', 'This ensures duplicate numbers do not generate the same permutation in a different order.'),
                qa('What role does sorting play?', 'Sorting groups duplicates together so the skip condition can identify equivalent placements.'),
            ],
        },
        {
            'id': 7,
            'leetcode_number': 46,
            'title': 'Permutations',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/permutations/',
            'problem_statement': 'Given an array nums of distinct integers, return all possible permutations in any order.',
            'examples': [
                {'input': 'nums = [1,2,3]', 'output': '[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]', 'explanation': 'All distinct permutations.'},
                {'input': 'nums = [0,1]', 'output': '[[0,1],[1,0]]', 'explanation': 'Two permutations for two elements.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 6', 'All integers are distinct.'],
            'intuition': 'Use backtracking to choose an unused number at each position until the permutation is complete.',
            'approaches': [
                approach(
                    'DFS with Used Array',
                    'Optimal',
                    'green',
                    'Mark numbers as used while building the current permutation and backtrack when the permutation is complete.',
                    'O(n!)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, new boolean[nums.length], new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] nums, boolean[] used, List<Integer> current, List<List<Integer>> result) {
        if (current.size() == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            used[i] = true;
            current.add(nums[i]);
            backtrack(nums, used, current, result);
            current.remove(current.size() - 1);
            used[i] = false;
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why use a used array instead of swapping?', 'A used array keeps the code straightforward and avoids in-place mutation when values are needed in original order.'),
                qa('What is the time complexity of generating all permutations?', 'There are n! permutations and each takes O(n) to build, so O(n·n!) total.'),
            ],
        },
        {
            'id': 8,
            'leetcode_number': 90,
            'title': 'Subsets II',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/subsets-ii/',
            'problem_statement': 'Given an integer array nums that may contain duplicates, return all possible subsets (the power set) without duplicate subsets.',
            'examples': [
                {'input': 'nums = [1,2,2]', 'output': '[[],[1],[1,2],[1,2,2],[2],[2,2]]', 'explanation': 'Subsets are unique despite duplicate values.'},
                {'input': 'nums = [0]', 'output': '[[],[0]]', 'explanation': 'Single element yields two subsets.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10', '-10 ≤ nums[i] ≤ 10'],
            'intuition': 'Sort the array and use backtracking, skipping duplicate values at the same recursion depth.',
            'approaches': [
                approach(
                    'Backtrack with Duplicate Skip',
                    'Optimal',
                    'green',
                    'Sort nums, then build subsets recursively while skipping identical values that would start duplicate branches.',
                    'O(2^n)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<Integer>> subsetsWithDup(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(nums);
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] nums, int start, List<Integer> current, List<List<Integer>> result) {
        result.add(new ArrayList<>(current));
        for (int i = start; i < nums.length; i++) {
            if (i > start && nums[i] == nums[i - 1]) continue;
            current.add(nums[i]);
            backtrack(nums, i + 1, current, result);
            current.remove(current.size() - 1);
        }
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why sort before backtracking?', 'Sorting groups duplicates so we can easily skip repeating branches.'),
                qa('Are empty subsets allowed?', 'Yes, the empty set is always included in the power set.'),
            ],
        },
        {
            'id': 9,
            'leetcode_number': 78,
            'title': 'Subsets',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/subsets/',
            'problem_statement': 'Given an integer array nums of unique elements, return all possible subsets (the power set).',
            'examples': [
                {'input': 'nums = [1,2,3]', 'output': '[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]', 'explanation': 'All subsets of the distinct set.'},
                {'input': 'nums = [0]', 'output': '[[],[0]]', 'explanation': 'Single element yields the empty and singleton subsets.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10', '-10 ≤ nums[i] ≤ 10', 'All nums are unique.'],
            'intuition': 'Backtrack by choosing whether to include each element, generating all 2^n subsets.',
            'approaches': [
                approach(
                    'Choose or Skip',
                    'Optimal',
                    'green',
                    'For each index, recursively explore both including and excluding the current element.',
                    'O(2^n)',
                    'O(n)',
                    None,
                    """class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] nums, int index, List<Integer> current, List<List<Integer>> result) {
        if (index == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }
        // Exclude current number
        backtrack(nums, index + 1, current, result);
        // Include current number
        current.add(nums[index]);
        backtrack(nums, index + 1, current, result);
        current.remove(current.size() - 1);
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('How many subsets does an n-element set have?', 'There are 2^n subsets, including the empty set and the set itself.'),
                qa('Why make copies of current?', 'Each leaf of recursion must keep its own subset independent of later changes during backtracking.'),
            ],
        },
        {
            'id': 10,
            'leetcode_number': 79,
            'title': 'Word Search',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/word-search/',
            'problem_statement': 'Given a 2D board and a word, return true if the word exists in the board by consecutive letters adjacent horizontally or vertically. You may not reuse the same cell twice.',
            'examples': [
                {'input': 'board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"', 'output': 'true', 'explanation': 'The word can be formed by a path through the board.'},
                {'input': 'board = [["a"]], word = "aa"', 'output': 'false', 'explanation': 'Cannot reuse the same cell twice.'},
            ],
            'constraints': ['m == board.length', 'n == board[i].length', '1 ≤ m, n ≤ 6', '1 ≤ word.length ≤ 15'],
            'intuition': 'Perform DFS from each cell and backtrack, marking visited cells so the current path does not reuse a position.',
            'approaches': [
                approach(
                    'DFS with Backtracking',
                    'Optimal',
                    'green',
                    'Start search from each board cell. Recursively match the word one letter at a time, marking visited cells and backtracking if needed.',
                    'O(m·n·4^L)',
                    'O(L)',
                    None,
                    """class Solution {
    public boolean exist(char[][] board, String word) {
        for (int i = 0; i < board.length; i++) {
            for (int j = 0; j < board[0].length; j++) {
                if (dfs(board, word, i, j, 0)) return true;
            }
        }
        return false;
    }

    private boolean dfs(char[][] board, String word, int i, int j, int index) {
        if (index == word.length()) return true;
        if (i < 0 || j < 0 || i >= board.length || j >= board[0].length) return false;
        if (board[i][j] != word.charAt(index)) return false;
        char c = board[i][j];
        board[i][j] = '#';
        boolean found = dfs(board, word, i + 1, j, index + 1)
            || dfs(board, word, i - 1, j, index + 1)
            || dfs(board, word, i, j + 1, index + 1)
            || dfs(board, word, i, j - 1, index + 1);
        board[i][j] = c;
        return found;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why mark visited cells and restore them?', 'Marking prevents cycles during one search path while restoring allows other starting points to reuse the cell.'),
                qa('What makes this search expensive?', 'The search branches in four directions at each step, so the worst-case complexity includes 4^L possibilities for a word of length L.'),
            ],
        },
    ],
    'binary-search': [
        {
            'id': 1,
            'leetcode_number': 704,
            'title': 'Binary Search',
            'difficulty': 'Easy',
            'url': 'https://leetcode.com/problems/binary-search/',
            'problem_statement': 'Given a sorted array of distinct integers and a target value, return the index if the target is found. Otherwise return -1.',
            'examples': [
                {'input': 'nums = [-1,0,3,5,9,12], target = 9', 'output': '4', 'explanation': '9 is found at index 4.'},
                {'input': 'nums = [-1,0,3,5,9,12], target = 2', 'output': '-1', 'explanation': '2 is not in the array.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 10⁴', '-10⁴ ≤ nums[i], target ≤ 10⁴', 'nums is sorted in ascending order and contains distinct values.'],
            'intuition': 'Use binary search to halve the search interval until you find the target or the interval is empty.',
            'approaches': [
                approach(
                    'Classic Binary Search',
                    'Optimal',
                    'green',
                    'Maintain left and right bounds, compare the middle element with the target, and move one bound inward based on the comparison.',
                    'O(log n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why compute mid as left + (right - left) / 2?', 'This avoids integer overflow when left and right are large.'),
                qa('What is the stopping condition?', 'Stop when left > right, which means the target is not present in the interval.'),
            ],
        },
        {
            'id': 2,
            'leetcode_number': 153,
            'title': 'Find Minimum in Rotated Sorted Array',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/',
            'problem_statement': 'Suppose an array sorted in ascending order is rotated at an unknown pivot. Find the minimum element in the array.',
            'examples': [
                {'input': 'nums = [3,4,5,1,2]', 'output': '1', 'explanation': 'The smallest item is 1 after rotation.'},
                {'input': 'nums = [4,5,6,7,0,1,2]', 'output': '0', 'explanation': '0 is the minimum.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 5000', '-10⁴ ≤ nums[i] ≤ 10⁴', 'All values are unique and the array is rotated at some pivot.'],
            'intuition': 'Use binary search by comparing mid to right. If mid > right, the minimum is in the right half; otherwise it is in the left half.',
            'approaches': [
                approach(
                    'Binary Search Pivot',
                    'Optimal',
                    'green',
                    'Track the sorted halves and narrow down the location of the minimum element using mid comparisons.',
                    'O(log n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int findMin(int[] nums) {
        int left = 0, right = nums.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] > nums[right]) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return nums[left];
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why compare mid with right?', 'The minimum is always in the half that contains the pivot between sorted segments.'),
                qa('Why not compare mid with left?', 'Comparing with right directly identifies whether mid is in the rotated tail or the sorted head.'),
            ],
        },
        {
            'id': 3,
            'leetcode_number': 162,
            'title': 'Find Peak Element',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/find-peak-element/',
            'problem_statement': 'Given an array where nums[i] != nums[i+1], find a peak element and return its index. A peak element is greater than its neighbors.',
            'examples': [
                {'input': 'nums = [1,2,3,1]', 'output': '2', 'explanation': 'nums[2] = 3 is a peak element.'},
                {'input': 'nums = [1,2,1,3,5,6,4]', 'output': '1 or 5', 'explanation': 'Either index with a local peak is acceptable.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 1000', 'nums[i] != nums[i+1] for all i.'],
            'intuition': 'Use binary search to move toward a rising slope. A peak exists where an element is larger than its neighbor.',
            'approaches': [
                approach(
                    'Binary Search on Slope',
                    'Optimal',
                    'green',
                    'If mid is lower than mid+1, a peak lies to the right; otherwise a peak lies to the left including mid.',
                    'O(log n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int findPeakElement(int[] nums) {
        int left = 0, right = nums.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] < nums[mid + 1]) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why is a peak guaranteed to exist?', 'The boundaries behave as if nums[-1] and nums[n] are -∞, so a peak must occur by the intermediate slope property.'),
                qa('Can either boundary be a peak?', 'Yes, a boundary can be a peak if it is greater than its single adjacent element.'),
            ],
        },
        {
            'id': 4,
            'leetcode_number': 875,
            'title': 'Koko Eating Bananas',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/koko-eating-bananas/',
            'problem_statement': 'Koko loves to eat bananas. Given piles of bananas and h hours, return the minimum eating speed k such that Koko can eat all bananas within h hours.',
            'examples': [
                {'input': 'piles = [3,6,7,11], h = 8', 'output': '4', 'explanation': 'Speed 4 allows finishing in 8 hours.'},
                {'input': 'piles = [30,11,23,4,20], h = 5', 'output': '30', 'explanation': 'The slowest possible speed to finish on time is 30.'},
            ],
            'constraints': ['1 ≤ piles.length ≤ 10⁴', '1 ≤ piles[i] ≤ 10⁹', 'piles.length ≤ h ≤ 10⁹'],
            'intuition': 'Binary search on the eating speed. For each speed, compute the hours needed and adjust the range accordingly.',
            'approaches': [
                approach(
                    'Binary Search on Answer',
                    'Optimal',
                    'green',
                    'Search for the smallest speed that finishes the piles within h hours.',
                    'O(n log m)',
                    'O(1)',
                    None,
                    """class Solution {
    public int minEatingSpeed(int[] piles, int h) {
        int left = 1, right = Arrays.stream(piles).max().getAsInt();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (canFinish(piles, mid, h)) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }

    private boolean canFinish(int[] piles, int speed, int h) {
        long hours = 0;
        for (int pile : piles) {
            hours += (pile + speed - 1) / speed;
            if (hours > h) return false;
        }
        return hours <= h;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why binary search on speed?', 'The time required decreases monotonically as speed increases, which makes the answer space searchable.'),
                qa('How do you compute hours for a pile?', 'Use ceiling division: (pile + speed - 1) / speed to count full hours needed.'),
            ],
        },
        {
            'id': 5,
            'leetcode_number': 4,
            'title': 'Median of Two Sorted Arrays',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/median-of-two-sorted-arrays/',
            'problem_statement': 'Given two sorted arrays, return the median of the combined array in O(log(m+n)) time.',
            'examples': [
                {'input': 'nums1 = [1,3], nums2 = [2]', 'output': '2.0', 'explanation': 'The merged array is [1,2,3].'},
                {'input': 'nums1 = [1,2], nums2 = [3,4]', 'output': '2.5', 'explanation': 'The merged array is [1,2,3,4].'},
            ],
            'constraints': ['nums1.length == m', 'nums2.length == n', '0 ≤ m, n ≤ 1000', '-10⁶ ≤ nums[i] ≤ 10⁶', 'The overall run time complexity should be O(log(m+n)).'],
            'intuition': 'Binary search on the smaller array to partition both arrays such that left halves and right halves satisfy median properties.',
            'approaches': [
                approach(
                    'Partition Binary Search',
                    'Optimal',
                    'green',
                    'Partition both arrays around the median and use the max left and min right values to compute the median.',
                    'O(log(min(m,n)))',
                    'O(1)',
                    None,
                    """class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        if (nums1.length > nums2.length) return findMedianSortedArrays(nums2, nums1);
        int m = nums1.length, n = nums2.length;
        int low = 0, high = m;
        while (low <= high) {
            int i = (low + high) / 2;
            int j = (m + n + 1) / 2 - i;
            int maxLeftA = (i == 0) ? Integer.MIN_VALUE : nums1[i - 1];
            int minRightA = (i == m) ? Integer.MAX_VALUE : nums1[i];
            int maxLeftB = (j == 0) ? Integer.MIN_VALUE : nums2[j - 1];
            int minRightB = (j == n) ? Integer.MAX_VALUE : nums2[j];
            if (maxLeftA <= minRightB && maxLeftB <= minRightA) {
                if ((m + n) % 2 == 1) {
                    return Math.max(maxLeftA, maxLeftB);
                }
                return (Math.max(maxLeftA, maxLeftB) + Math.min(minRightA, minRightB)) / 2.0;
            } else if (maxLeftA > minRightB) {
                high = i - 1;
            } else {
                low = i + 1;
            }
        }
        throw new IllegalArgumentException();
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why binary search the smaller array?', 'Binary searching the smaller array keeps the partition space minimal and avoids index issues.'),
                qa('How is the median computed from partition edges?', 'Use the larger of left-side maxima and the smaller of right-side minima, with one or two elements depending on parity.'),
            ],
        },
        {
            'id': 6,
            'leetcode_number': 74,
            'title': 'Search a 2D Matrix',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/search-a-2d-matrix/',
            'problem_statement': 'Write an efficient algorithm that searches for a target value in an m x n matrix with each row sorted and rows connected end-to-start.',
            'examples': [
                {'input': 'matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,50]], target = 3', 'output': 'true', 'explanation': '3 exists in the matrix.'},
                {'input': 'matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,50]], target = 13', 'output': 'false', 'explanation': '13 is not present.'},
            ],
            'constraints': ['m == matrix.length', 'n == matrix[i].length', '1 ≤ m, n ≤ 100', '-10⁴ ≤ matrix[i][j], target ≤ 10⁴', 'Each row is sorted and the first element of each row is greater than the last element of the previous row.'],
            'intuition': 'Treat the matrix as a flattened sorted array and use binary search on a virtual index.',
            'approaches': [
                approach(
                    'Virtual Flattened Binary Search',
                    'Optimal',
                    'green',
                    'Map a 1D index to 2D coordinates and binary search across the whole matrix.',
                    'O(log(mn))',
                    'O(1)',
                    None,
                    """class Solution {
    public boolean searchMatrix(int[][] matrix, int target) {
        int m = matrix.length;
        int n = matrix[0].length;
        int left = 0, right = m * n - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            int midValue = matrix[mid / n][mid % n];
            if (midValue == target) return true;
            if (midValue < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return false;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('How do you map the 1D index to the matrix?', 'Row = index / n and column = index % n if n is the number of columns.'),
                qa('Why is the matrix treated as sorted?', 'The row-wise ordering and the condition between rows make the flattened array globally sorted.'),
            ],
        },
        {
            'id': 7,
            'leetcode_number': 81,
            'title': 'Search in Rotated Sorted Array II',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/search-in-rotated-sorted-array-ii/',
            'problem_statement': 'Search a target value in a rotated sorted array that may contain duplicates. Return true if the target exists.',
            'examples': [
                {'input': 'nums = [2,5,6,0,0,1,2], target = 0', 'output': 'true', 'explanation': '0 exists in the array.'},
                {'input': 'nums = [2,5,6,0,0,1,2], target = 3', 'output': 'false', 'explanation': '3 is not present.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 5000', '-10⁴ ≤ nums[i], target ≤ 10⁴'],
            'intuition': 'Modified binary search handles duplicates by shrinking the search interval when the ordered half cannot be determined.',
            'approaches': [
                approach(
                    'Binary Search with Duplicates',
                    'Optimal',
                    'green',
                    'Compare mid to left and right to determine which half is sorted, and skip duplicates when ambiguous.',
                    'O(n) worst case',
                    'O(1)',
                    None,
                    """class Solution {
    public boolean search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return true;
            if (nums[left] == nums[mid] && nums[mid] == nums[right]) {
                left++;
                right--;
            } else if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return false;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why can this degrade to O(n)?', 'When duplicates hide the sorted half, the algorithm may need to shrink the interval linearly.'),
                qa('What if left, mid, and right are equal?', 'In that case, move both bounds inward to reduce ambiguity.'),
            ],
        },
        {
            'id': 8,
            'leetcode_number': 33,
            'title': 'Search in Rotated Sorted Array',
            'difficulty': 'Medium',
            'url': 'https://leetcode.com/problems/search-in-rotated-sorted-array/',
            'problem_statement': 'Search a target value in a rotated sorted array with distinct elements. Return its index if found, otherwise return -1.',
            'examples': [
                {'input': 'nums = [4,5,6,7,0,1,2], target = 0', 'output': '4', 'explanation': 'The target 0 is at index 4.'},
                {'input': 'nums = [4,5,6,7,0,1,2], target = 3', 'output': '-1', 'explanation': '3 is not found.'},
            ],
            'constraints': ['1 ≤ nums.length ≤ 5000', '-10⁴ ≤ nums[i], target ≤ 10⁴', 'All values are unique.'],
            'intuition': 'Determine which half of the rotated array is sorted and decide whether the target lies there.',
            'approaches': [
                approach(
                    'Binary Search on Rotated Array',
                    'Optimal',
                    'green',
                    'At each step, identify the sorted half and restrict search to the half that may contain the target.',
                    'O(log n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return -1;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('How do you know which half is sorted?', 'Compare nums[left] and nums[mid]. If left ≤ mid, the left half is sorted; otherwise the right half is sorted.'),
                qa('Why check target against the sorted half?', 'The target can only be present in the sorted half if it lies between its endpoints.'),
            ],
        },
    ],
    'design': [
        {
            'id': 1,
            'leetcode_number': 432,
            'title': 'All O`1` Data Structure',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/all-oone-data-structure/',
            'problem_statement': 'Design a data structure supporting increment, decrement, getMaxKey, and getMinKey operations all in O(1) time.',
            'examples': [
                {'input': 'Operations include inc("a"), inc("b"), inc("b"), getMaxKey(), getMinKey()', 'output': '"b", "a"', 'explanation': 'b has highest count, a has lowest count.'},
                {'input': 'After decrementing and removing keys, getMaxKey() and getMinKey() return empty strings.', 'output': '"", ""', 'explanation': 'No keys remain.'},
            ],
            'constraints': ['At most 5·10⁴ operations.', 'Keys are non-empty strings of lowercase letters.'],
            'intuition': 'Use a doubly linked list of count buckets and a hash map from keys to nodes so counts can be updated and extremes can be read in O(1).',
            'approaches': [
                approach(
                    'Bucket List with HashMaps',
                    'Optimal',
                    'green',
                    'Maintain a linked list of frequency nodes and a map from keys to their bucket to support constant-time updates.',
                    'O(1)',
                    'O(n)',
                    None,
                    """class AllOne {
    private static class Node {
        int count;
        Set<String> keys = new HashSet<>();
        Node prev, next;
    }

    private final Node head = new Node();
    private final Node tail = new Node();
    private final Map<String, Node> keyToNode = new HashMap<>();

    public AllOne() {
        head.next = tail;
        tail.prev = head;
    }

    public void inc(String key) {
        Node node = keyToNode.getOrDefault(key, head);
        Node next = node.next;
        if (next == tail || next.count != node.count + 1) {
            next = insertAfter(node, node.count + 1);
        }
        next.keys.add(key);
        keyToNode.put(key, next);
        if (node != head) {
            node.keys.remove(key);
            if (node.keys.isEmpty()) remove(node);
        }
    }

    public void dec(String key) {
        Node node = keyToNode.get(key);
        if (node == null) return;
        if (node.count == 1) {
            keyToNode.remove(key);
        } else {
            Node prev = node.prev;
            if (prev == head || prev.count != node.count - 1) {
                prev = insertAfter(node.prev, node.count - 1);
            }
            prev.keys.add(key);
            keyToNode.put(key, prev);
        }
        node.keys.remove(key);
        if (node.keys.isEmpty()) remove(node);
    }

    public String getMaxKey() {
        return tail.prev == head ? "" : tail.prev.keys.iterator().next();
    }

    public String getMinKey() {
        return head.next == tail ? "" : head.next.keys.iterator().next();
    }

    private Node insertAfter(Node node, int count) {
        Node newNode = new Node();
        newNode.count = count;
        newNode.next = node.next;
        newNode.prev = node;
        node.next.prev = newNode;
        node.next = newNode;
        return newNode;
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
} // simplified for clarity""",
                ),
            ],
            'interview_qa': [
                qa('Why use a linked list of buckets?', 'It lets you move keys between counts and still access min/max counts in constant time.'),
                qa('What does the key-to-node map store?', 'It stores current bucket references for each key to update counts quickly.'),
            ],
        },
        {
            'id': 2,
            'leetcode_number': 233,
            'title': 'Number of Digit One',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/number-of-digit-one/',
            'problem_statement': 'Given an integer n, count the occurrences of the digit one in all non-negative integers less than or equal to n.',
            'examples': [
                {'input': 'n = 13', 'output': '6', 'explanation': 'The numbers are 1,10,11,12,13.'},
                {'input': 'n = 0', 'output': '0', 'explanation': 'No ones appear.'},
            ],
            'constraints': ['0 ≤ n ≤ 10⁹'],
            'intuition': 'Count contributions of each digit place separately by analyzing higher and lower parts around the current digit.',
            'approaches': [
                approach(
                    'Place Value Counting',
                    'Optimal',
                    'green',
                    'For each digit position, calculate how many full cycles and partial cycles contribute a 1 at that position.',
                    'O(log n)',
                    'O(1)',
                    None,
                    """class Solution {
    public int countDigitOne(int n) {
        long factor = 1;
        int count = 0;
        while (factor <= n) {
            int lower = (int)(n - (n / factor) * factor);
            int curr = (int)((n / factor) % 10);
            int higher = (int)(n / (factor * 10));
            if (curr == 0) {
                count += higher * factor;
            } else if (curr == 1) {
                count += higher * factor + lower + 1;
            } else {
                count += (higher + 1) * factor;
            }
            factor *= 10;
        }
        return count;
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('What are full cycles and partial cycles?', 'Full cycles are complete 0..9 repeats at a digit position, partial cycles cover the remainder once the current digit is fixed.'),
                qa('Why analyze each digit position separately?', 'The frequency of a digit depends on its place value and how the number spans across powers of ten.'),
            ],
        },
        {
            'id': 3,
            'leetcode_number': 124,
            'title': 'Binary Tree Maximum Path Sum',
            'difficulty': 'Hard',
            'url': 'https://leetcode.com/problems/binary-tree-maximum-path-sum/',
            'problem_statement': 'Given a binary tree, return the maximum path sum. A path can start and end at any node and must contain at least one node.',
            'examples': [
                {'input': 'root = [1,2,3]', 'output': '6', 'explanation': 'The path 2 → 1 → 3 has sum 6.'},
                {'input': 'root = [-10,9,20,null,null,15,7]', 'output': '42', 'explanation': 'The path 15 → 20 → 7 has sum 42.'},
            ],
            'constraints': ['The number of nodes is in the range [1, 3·10⁴].', '-1000 ≤ Node.val ≤ 1000'],
            'intuition': 'At each node, compute the maximum path sum extending downward and track the best path that passes through the node.',
            'approaches': [
                approach(
                    'Post-order DFS',
                    'Optimal',
                    'green',
                    'Compute the maximum gain from left and right children, then update the global best path including the current node.',
                    'O(n)',
                    'O(n)',
                    None,
                    """class Solution {
    private int best = Integer.MIN_VALUE;
    public int maxPathSum(TreeNode root) {
        dfs(root);
        return best;
    }

    private int dfs(TreeNode node) {
        if (node == null) return 0;
        int left = Math.max(0, dfs(node.left));
        int right = Math.max(0, dfs(node.right));
        best = Math.max(best, node.val + left + right);
        return node.val + Math.max(left, right);
    }
}""",
                ),
            ],
            'interview_qa': [
                qa('Why ignore negative child contributions?', 'Negative gains reduce the path sum, so treat them as zero when extending upward.'),
                qa('What is the global best representing?', 'It records the maximum path sum for any path that passes through a node and potentially includes both children.'),
            ],
        },
    ],
    # Remaining topics omitted for brevity in this creation script placeholder; they will be generated similarly.
}


def normalize_title_to_filename(title):
    filename = title.lower()
    for ch in [' ', '`', '’', '?', '!', '"', ',', ':', '\'', '&', '/', '(', ')']:
        filename = filename.replace(ch, '-')
    while '--' in filename:
        filename = filename.replace('--', '-')
    filename = filename.strip('-')
    return f'{filename}.json'


def title_to_statement(title):
    if not title:
        return 'Implement the problem using the standard topic approach.'
    title_lower = title.lower()
    exact = {
        'house robber': 'Rob houses such that adjacent houses are not robbed on the same night and maximize total stolen value.',
        'house robber ii': 'Rob houses arranged in a circle, maximizing stolen value without robbing adjacent houses.',
        'climbing stairs': 'Count distinct ways to climb n stairs when you can take one or two steps at a time.',
        'coin change': 'Return the fewest number of coins needed to make up the target from an unlimited supply of denominations.',
        'coin change iv': 'Count the number of combinations to make the target using unlimited coins.',
        'decode ways': 'Count the number of ways to decode a digit string into letters using 1→A through 26→Z.',
        'distinct subsequences': 'Count how many distinct subsequences of s equal t.',
        'edit distance': 'Compute the minimum number of operations to convert one string into another.',
        'interleaving string': 'Determine whether s3 is formed by interleaving s1 and s2 while preserving order.',
        'jump game': 'Return true if you can reach the last index using jump lengths specified by the array.',
        'jump game ii': 'Return the minimum number of jumps needed to reach the last index.',
        'longest common subsequence': 'Find the length of the longest subsequence common to both strings.',
        'longest increasing subsequence': 'Return the length of the longest strictly increasing subsequence in the array.',
        'maximal square': 'Find the largest square containing only 1s in a binary matrix and return its area.',
        'minimum path sum': 'Compute the minimum path sum from the top-left to bottom-right of a grid.',
        'partition equal subset sum': 'Return whether the array can be partitioned into two subsets with equal sum.',
        'regular expression matching': 'Implement full regex matching for patterns with . and *.',
        'target sum': 'Count ways to assign + or - to make the sum of numbers equal the target.',
        'unique paths': 'Count unique paths from top-left to bottom-right of a grid moving only right and down.',
        'word break': 'Determine if the string can be segmented into a sequence of dictionary words.',
        'accounts merge union find': 'Merge accounts that share common email addresses into unique account groups.',
        'cheapest flights within k stops': 'Find the cheapest flight cost from src to dst with at most k stops.',
        'clone graph': 'Return a deep copy of the given undirected graph.',
        'course schedule': 'Determine if you can finish all courses given prerequisite pairs.',
        'course schedule ii': 'Return a valid order of courses given prerequisites, or an empty list if impossible.',
        'evaluate division': 'Evaluate division queries based on known ratios between variables.',
        'graph valid tree': 'Determine whether the edges form a valid tree on the given nodes.',
        'max area of island': 'Find the size of the largest island in a grid of 0s and 1s.',
        'network delay time': 'Compute how long it takes for all nodes to receive a signal from the source.',
        'number of connected components union find': 'Return the number of connected components in an undirected graph.',
        'number of islands': 'Count islands in a grid of water and land cells.',
        'pacific atlantic water flow': 'Return cells that can flow to both the Pacific and Atlantic oceans.',
        'redundant connection union find': 'Find the extra edge that creates a cycle in an otherwise tree graph.',
        'rotting oranges': 'Return how many minutes until all fresh oranges rot or -1 if impossible.',
        'surrounded regions': 'Capture regions of Os surrounded by Xs on the board.',
        'walls and gates': 'Fill each empty room with the distance to its nearest gate.',
        'word ladder': 'Return the shortest transformation length from beginWord to endWord by changing one letter at a time.',
        'word ladder ii': 'Return all shortest transformation sequences from beginWord to endWord by changing one letter at a time.',
        'best time to buy and sell stock': 'Return the maximum profit from one buy-sell transaction.',
        'gas station': 'Determine if there is a starting gas station to complete the circuit.',
        'merge triplets to form target triplet': 'Check whether you can merge triplets to form the target triplet by taking component-wise maxes.',
        'minimum number of arrows to burst balloons': 'Return the minimum number of arrows needed to burst all balloons represented by intervals.',
        'partition labels': 'Partition a string into as many parts as possible so each letter appears in at most one part.',
        'find median from data stream': 'Maintain a data structure that returns the median from a stream of numbers.',
        'k closest points to origin': 'Return the k points closest to the origin by Euclidean distance.',
        'kth largest element in an array': 'Return the kth largest element in an unsorted array.',
        'last stone weight': 'Simulate smashing the two largest stones until at most one stone remains and return its weight.',
        'merge k sorted lists': 'Merge k sorted linked lists into one sorted list.',
        'reorganize string': 'Rearrange the string so no two adjacent characters are the same if possible.',
        'task scheduler': 'Schedule tasks with cooldown intervals to minimize total time.',
        'top k frequent elements': 'Return the k most frequent elements in the array.',
        'insert interval': 'Insert a new interval into sorted non-overlapping intervals and merge if necessary.',
        'meeting rooms': 'Determine whether a person can attend all given intervals without overlaps.',
        'meeting rooms ii': 'Return the minimum number of conference rooms required for all intervals.',
        'merge intervals': 'Merge overlapping intervals into a list of disjoint intervals.',
        'non overlapping intervals': 'Return the minimum number of intervals to remove so the rest do not overlap.',
        'add two numbers': 'Add two numbers represented as reversed linked lists and return the sum as a linked list.',
        'copy list with random pointer': 'Return a deep copy of a linked list where each node has a random pointer.',
        'flatten a multilevel doubly linked list': 'Flatten a multilevel doubly linked list into a single-level doubly linked list.',
        'intersection of two linked lists': 'Return the node where two singly linked lists intersect, if any.',
        'linked list cycle': 'Detect whether a linked list contains a cycle.',
        'merge two sorted lists': 'Merge two sorted linked lists into one sorted list.',
        'remove nth node from end of list': 'Remove the nth node from the end of a linked list and return the head.',
        'reorder list': 'Reorder a linked list from L0→Ln→L1→Ln-1→... layout.',
        'reverse linked list': 'Reverse a singly linked list and return the head.',
        'counting bits': 'Return the number of 1 bits in the binary representation for each number from 0 to n.',
        'happy number': 'Determine whether a number eventually reaches 1 when replaced by the sum of squares of its digits.',
        'number of 1 bits': 'Return the number of 1 bits in the binary representation of an unsigned integer.',
        'reverse bits': 'Reverse the bits of a 32-bit unsigned integer.',
        'sum of two integers': 'Compute the sum of two integers without using + or - operators.',
        'find all anagrams in a string': 'Return all starting indices of p’s anagrams in s.',
        'longest repeating character replacement': 'Find the length of the longest substring achievable by replacing up to k characters.',
        'longest subarray with ones after replacement': 'Return the longest subarray containing only 1s after replacing up to k zeros.',
        'longest substring without repeating characters': 'Return the length of the longest substring without repeating characters.',
        'maximum average subarray i': 'Return the maximum average value of any contiguous subarray of length k.',
        'minimum window substring': 'Find the smallest substring containing all characters of t.',
        'permutation in string': 'Determine whether s2 contains a permutation of s1 as a substring.',
        'sliding window maximum': 'Return the maximum value in each sliding window of size k.',
        'car fleet': 'Count how many car fleets will reach the destination given positions and speeds.',
        'daily temperatures': 'Return the number of days until a warmer temperature for each day.',
        'evaluate reverse polish notation': 'Evaluate the value of an arithmetic expression given in Reverse Polish Notation.',
        'generate parentheses': 'Generate all combinations of well-formed parentheses for n pairs.',
        'largest rectangle in histogram': 'Calculate the area of the largest rectangle in a histogram.',
        'min stack': 'Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.',
        'valid parentheses': 'Determine whether the input string of brackets is valid and properly closed.',
        'binary tree level order traversal': 'Return the level order traversal of a binary tree.',
        'binary tree maximum path sum': 'Return the maximum path sum of any path in a binary tree.',
        'construct binary tree from preorder and inorder traversal': 'Reconstruct a binary tree from its preorder and inorder traversals.',
        'count good nodes in binary tree': 'Count nodes that are greater than or equal to all values on the path from the root.',
        'diameter of binary tree': 'Return the length of the diameter of the binary tree.',
        'invert binary tree': 'Invert a binary tree by swapping left and right children.',
        'kth smallest element in a bst': 'Return the kth smallest element in a binary search tree.',
        'lowest common ancestor of a bst': 'Find the lowest common ancestor of two nodes in a BST.',
        'maximum depth of binary tree': 'Return the maximum depth of the binary tree.',
        'path sum ii': 'Return all root-to-leaf paths where the sum equals the target.',
        'same tree': 'Determine whether two binary trees are structurally identical with equal values.',
        'serialize and deserialize binary tree': 'Design methods to serialize and deserialize a binary tree to and from a string.',
        'subtree of another tree': 'Determine whether one tree is a subtree of another.',
        'validate binary search tree': 'Determine whether a binary tree is a valid BST.',
        'add and search word': 'Design a data structure that supports adding words and searching with dot wildcards.',
        'implement trie prefix tree': 'Implement a trie with insert, search, and startsWith operations.',
        'word search ii': 'Return all words from the dictionary that can be formed in the board by adjacent letters.',
        '3sum': 'Return all unique triplets in the array that add up to zero.',
        'container with most water': 'Find the maximum area formed by vertical lines in the array.',
        'remove duplicates from sorted array': 'Remove duplicates in place and return the new length of the array.',
        'trapping rain water': 'Compute how much rain water can be trapped by bars in the elevation map.',
        'two sum ii': 'Find two numbers in a sorted array that add up to the target and return their indices.',
        'valid palindrome': 'Determine whether a string is a palindrome after removing non-alphanumeric characters and ignoring case.',
        'design file system': 'Design a file system that supports creating paths with values and retrieving values using path strings.',
        'design twitter': 'Design a simple social media service supporting posting tweets, following users, and retrieving a user’s news feed.',
        'encode and decode strings': 'Design an algorithm to encode a list of strings to a single string and decode it back without ambiguity.',
        'insert delete getrandom o(1)': 'Design a data structure that supports insert, delete, and getRandom in average O(1) time.',
        'lfu cache': 'Design and implement a Least Frequently Used (LFU) cache with get and put operations in O(1) time.',
        'lru cache': 'Design and implement a Least Recently Used (LRU) cache with get and put operations in O(1) time.',
        'random pick with weight': 'Design a function that randomly picks an index from an array with probability proportional to its weight.',
        'search suggestions system': 'Build a search suggestion system that returns up to three lexicographically sorted product names matching a search prefix.',
        'time based key value store': 'Design a time-based key-value store supporting set and get operations with timestamps.',
        'burst balloons': 'Given balloons with values, maximize coins by bursting them in an order where each burst yields the product of adjacent balloon values.',
        'climbing stairs': 'Count the distinct ways to climb n stairs if you can take 1 or 2 steps each time.',
        'coin change': 'Given a set of coin denominations and a target amount, find the fewest coins needed to make the amount.',
        'decode ways': 'Given a string of digits, count the number of ways to decode it into letters using mapping 1->A to 26->Z.',
        'distinct subsequences': 'Count the number of distinct ways to form string t from string s by deleting characters without changing order.',
        'edit distance': 'Compute the minimum number of insertions, deletions, and substitutions to convert word1 into word2.',
        'house robber': 'Maximize the amount of money robbed from a line of houses without robbing adjacent houses.',
        'house robber ii': 'Maximize the amount robbed from a circular arrangement of houses without robbing two adjacent houses.',
        'interleaving string': 'Determine whether s3 is formed by interleaving s1 and s2 while preserving the relative order of characters.',
        'jump game': 'Determine whether you can reach the last index of the array given maximum jump lengths from each position.',
        'longest common subsequence': 'Find the length of the longest subsequence common to two strings.',
        'longest increasing subsequence': 'Find the length of the longest strictly increasing subsequence in an integer array.',
        'minimum path sum': 'Find the minimum sum path from the top-left corner to the bottom-right corner of a grid moving only down or right.',
        'partition equal subset sum': 'Determine whether the array can be partitioned into two subsets with equal sum.',
        'regular expression matching': 'Implement regular expression matching with support for "." and "*", where "." matches any character and "*" matches zero or more of the preceding element.',
        'target sum': 'Count the number of ways to assign plus or minus signs to array elements to reach a target sum.',
        'unique paths': 'Count the number of unique paths from the top-left corner to the bottom-right corner in an m x n grid moving only down or right.',
        'word break': 'Determine whether the string can be segmented into a sequence of one or more dictionary words.',
        'accounts merge union find': 'Merge user accounts by matching email addresses and return unique account groups.',
        'cheapest flights within k stops': 'Find the cheapest flight cost from source to destination with at most k stops.',
        'clone graph': 'Return a deep copy of an undirected graph given a reference node.',
        'course schedule': 'Determine whether all courses can be finished given prerequisite pairs between courses.',
        'course schedule ii': 'Return a valid order to finish all courses given prerequisite pairs or an empty list if impossible.',
        'evaluate division': 'Evaluate division queries given equations relating variable ratios.',
        'graph valid tree': 'Determine whether an undirected graph with n nodes and edges forms a valid tree.',
        'max area of island': 'Return the maximum area of an island in a binary grid, where islands are groups of connected 1s.',
        'network delay time': 'Compute how long it will take for all nodes to receive a signal sent from a starting node in a weighted directed graph.',
        'number of connected components union find': 'Count the number of connected components in an undirected graph.',
        'number of islands': 'Count the distinct islands in a grid, where islands are regions of adjacent 1s.',
        'pacific atlantic water flow': 'Find grid cells where water can flow to both the Pacific and Atlantic oceans given height constraints.',
        'redundant connection union find': 'Find the edge whose removal makes the given undirected graph a tree.',
        'rotting oranges': 'Determine the minimum minutes until all fresh oranges become rotten given rot spreads to adjacent oranges each minute.',
        'surrounded regions': 'Capture all regions of Os fully surrounded by Xs in a board by flipping them to Xs.',
        'walls and gates': 'Fill each empty room with its distance to the nearest gate in a grid of rooms, walls, and gates.',
        'word ladder': 'Return the length of the shortest transformation sequence from beginWord to endWord by changing one letter at a time.',
        'word ladder ii': 'Find all shortest transformation sequences from beginWord to endWord using a word list.',
        'best time to buy and sell stock': 'Maximize profit from a single buy-sell transaction on stock prices.',
        'gas station': 'Find the starting gas station index from which you can complete the circuit given gas and costs.',
        'jump game ii': 'Return the minimum number of jumps needed to reach the last index.',
        'merge triplets to form target triplet': 'Check whether you can form a target triplet by merging selected triplets component-wise.',
        'minimum number of arrows to burst balloons': 'Find the minimum number of arrows needed to burst all balloons represented as intervals.',
        'partition labels': 'Partition a string into as many parts as possible so that each letter appears in at most one part.',
        'find median from data stream': 'Continuously add numbers from a stream and return the median after each insertion.',
        'k closest points to origin': 'Return the k points closest to the origin by Euclidean distance.',
        'kth largest element in an array': 'Find the kth largest element in an unsorted array.',
        'last stone weight': 'Simulate smashing the two heaviest stones until at most one remains and return its weight.',
        'merge k sorted lists': 'Merge k sorted linked lists into one sorted list.',
        'reorganize string': 'Rearrange a string so that no two adjacent characters are the same, or return an empty string if impossible.',
        'task scheduler': 'Schedule tasks with cooling intervals and return the minimum number of intervals required to finish all tasks.',
        'top k frequent elements': 'Return the k most frequent elements from an array.',
        'insert interval': 'Insert a new interval into a list of non-overlapping intervals and merge overlapping intervals if necessary.',
        'meeting rooms': 'Determine if a person can attend all meetings given their time intervals.',
        'meeting rooms ii': 'Find the minimum number of conference rooms required to host all meetings.',
        'merge intervals': 'Merge all overlapping intervals and return the resulting set of disjoint intervals.',
        'non-overlapping intervals': 'Remove the minimum number of intervals to make the rest non-overlapping.',
        'add two numbers': 'Add two numbers represented by linked lists where digits are stored in reverse order and return the sum as a linked list.',
        'copy list with random pointer': 'Copy a linked list where each node has an extra random pointer in addition to the next pointer.',
        'flatten a multilevel doubly linked list': 'Flatten a multilevel doubly linked list to a single-level doubly linked list.',
        'intersection of two linked lists': 'Return the node where two singly linked lists intersect, or null if no intersection exists.',
        'linked list cycle': 'Detect whether a linked list contains a cycle.',
        'merge two sorted lists': 'Merge two sorted linked lists into one sorted linked list.',
        'remove nth node from end of list': 'Remove the nth node from the end of a linked list and return the new head.',
        'reorder list': 'Reorder a linked list to L0→Ln→L1→Ln-1… in-place.',
        'reverse linked list': 'Reverse a singly linked list.',
        'counting bits': 'Return an array where each element is the number of 1 bits in the binary representation of the corresponding index.',
        'happy number': 'Determine whether a number eventually reaches 1 when replaced by the sum of squares of its digits.',
        'number of 1 bits': 'Return the number of 1 bits in the binary representation of an unsigned integer.',
        'reverse bits': 'Reverse the bits of a 32-bit unsigned integer.',
        'sum of two integers': 'Compute the sum of two integers without using + or - operators.',
        'longest repeating character replacement': 'Find the length of the longest substring achievable by replacing up to k characters.',
        'longest subarray with ones after replacement': 'Return the longest subarray containing only 1s after replacing up to k zeros.',
        'longest substring without repeating characters': 'Return the length of the longest substring without repeating characters.',
        'maximum average subarray i': 'Return the maximum average value of any contiguous subarray of length k.',
        'minimum window substring': 'Find the smallest substring containing all characters of t.',
        'permutation in string': 'Determine whether s2 contains a permutation of s1 as a substring.',
        'sliding window maximum': 'Return the maximum value in each sliding window of size k.',
        'car fleet': 'Count how many car fleets will reach the destination given positions and speeds.',
        'daily temperatures': 'Return the number of days until a warmer temperature for each day.',
        'evaluate reverse polish notation': 'Evaluate the value of an arithmetic expression given in Reverse Polish Notation.',
        'generate parentheses': 'Generate all combinations of well-formed parentheses for n pairs.',
        'largest rectangle in histogram': 'Calculate the area of the largest rectangle in a histogram.',
        'min stack': 'Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.',
        'valid parentheses': 'Determine whether the input string of brackets is valid and properly closed.',
        'binary tree level order traversal': 'Return the level order traversal of a binary tree.',
        'binary tree maximum path sum': 'Return the maximum path sum of any path in a binary tree.',
        'construct binary tree from preorder and inorder traversal': 'Reconstruct a binary tree from its preorder and inorder traversals.',
        'count good nodes in binary tree': 'Count nodes that are greater than or equal to all values on the path from the root.',
        'diameter of binary tree': 'Return the length of the diameter of the binary tree.',
        'invert binary tree': 'Invert a binary tree by swapping left and right children.',
        'kth smallest element in a bst': 'Return the kth smallest element in a binary search tree.',
        'lowest common ancestor of a bst': 'Find the lowest common ancestor of two nodes in a BST.',
        'maximum depth of binary tree': 'Return the maximum depth of the binary tree.',
        'path sum ii': 'Return all root-to-leaf paths where the sum equals the target.',
        'same tree': 'Determine whether two binary trees are structurally identical with equal values.',
        'serialize and deserialize binary tree': 'Design methods to serialize and deserialize a binary tree to and from a string.',
        'subtree of another tree': 'Determine whether one tree is a subtree of another.',
        'validate binary search tree': 'Determine whether a binary tree is a valid BST.',
        'add and search word': 'Design a data structure that supports adding words and searching with dot wildcards.',
        'implement trie prefix tree': 'Implement a trie with insert, search, and startsWith operations.',
        '3sum': 'Return all unique triplets in the array that add up to zero.',
        'container with most water': 'Find the maximum area formed by vertical lines in the array.',
        'remove duplicates from sorted array': 'Remove duplicates in place and return the new length of the array.',
        'trapping rain water': 'Compute how much rain water can be trapped by bars in the elevation map.',
        'two sum ii': 'Find two numbers in a sorted array that add up to the target and return their indices.',
        'valid palindrome': 'Determine whether a string is a palindrome after removing non-alphanumeric characters and ignoring case.',
    }
    return exact.get(title_lower, f'Implement the problem "{title}" using a standard topic-specific approach.')


def title_to_examples(title):
    title_lower = title.lower()
    examples = {
        'house robber': [
            example('nums = [1,2,3,1]', '4', 'Rob houses 1 and 3 for maximum value.'),
        ],
        'house robber ii': [
            example('nums = [2,3,2]', '3', 'Choose the best circular arrangement without adjacent houses.'),
        ],
        'climbing stairs': [
            example('n = 3', '3', 'Three ways: 1+1+1, 1+2, 2+1.'),
        ],
        'coin change': [
            example('coins = [1,2,5], amount = 11', '3', 'Use 5+5+1 for the fewest coins.'),
        ],
        'decode ways': [
            example('s = "12"', '2', 'AB or L.'),
        ],
        'edit distance': [
            example('word1 = "horse", word2 = "ros"', '3', 'Remove h, replace r, remove e.'),
        ],
        'word break': [
            example('s = "leetcode", wordDict = ["leet","code"]', 'true', 'The string can be segmented as leet code.'),
        ],
        'course schedule': [
            example('numCourses = 2, prerequisites = [[1,0]]', 'true', 'Course 0 must be taken before 1.'),
        ],
        'course schedule ii': [
            example('numCourses = 2, prerequisites = [[1,0]]', '[0,1]', 'Return a valid course ordering.'),
        ],
        'number of islands': [
            example('grid = [["1","1","0"],["1","0","0"],["0","0","1"]]', '2', 'There are two separate islands.'),
        ],
        'minimum window substring': [
            example('s = "ADOBECODEBANC", t = "ABC"', 'BANC', 'Smallest window containing A, B, and C.'),
        ],
        'valid parentheses': [
            example('s = "()[]{}"', 'true', 'All brackets are valid and properly nested.'),
        ],
        'find median from data stream': [
            example('addNum(1), addNum(2), findMedian()', '1.5', 'Median of [1,2] is 1.5.'),
        ],
        'generate parentheses': [
            example('n = 3', '["((()))","(()())","(())()","()(())","()()()" ]', 'Generate all valid parentheses.'),
        ],
        'search a 2d matrix': [
            example('matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,50]], target = 3', 'true', 'The target is found in the matrix.'),
        ],
        'search in rotated sorted array': [
            example('nums = [4,5,6,7,0,1,2], target = 0', '4', 'Find the target index in a rotated sorted array.'),
        ],
        'search in rotated sorted array ii': [
            example('nums = [2,5,6,0,0,1,2], target = 0', 'true', 'The target exists even with duplicates.'),
        ],
        'two sum ii': [
            example('numbers = [2,7,11,15], target = 9', '[1,2]', 'Return 1-indexed indices of the pair.'),
        ],
        'kth largest element in an array': [
            example('nums = [3,2,1,5,6,4], k = 2', '5', 'The 2nd largest element is 5.'),
        ],
        'merge k sorted lists': [
            example('lists = [[1,4,5],[1,3,4],[2,6]]', '[1,1,2,3,4,4,5,6]', 'Merge all sorted lists into one list.'),
        ],
        'permutations': [
            example('nums = [1,2,3]', '[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]', 'Return all permutations.'),
        ],
        'subsets': [
            example('nums = [1,2,3]', '[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]', 'All subsets of the array.'),
        ],
        'word ladder': [
            example('beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]', '5', 'Shortest transformation length is 5.'),
        ],
        'design file system': [
            example('createPath("/a", 1), get("/a")', '1', 'Support createPath and get operations.'),
        ],
        'design twitter': [
            example('postTweet(1, 5), follow(1,2), getNewsFeed(1)', '[5]', 'Return user 1’s news feed after posting and following.'),
        ],
        'encode and decode strings': [
            example('[

def generic_approach(topic):
    topic_map = {
        'arrays-hashing': ('Use hash-based storage for fast lookup and counting.', 'O(n)', 'O(n)'),
        'backtracking': ('Recursively build candidates and backtrack on dead ends.', 'O(2^n)', 'O(n)'),
        'binary-search': ('Use binary search or binary-search-on-answer patterns.', 'O(log n)', 'O(1)'),
        'design': ('Choose data structures that support the required API in constant time.', 'O(1)', 'O(n)'),
        'dynamic-programming': ('Define subproblem state and reuse results via memoization or tabulation.', 'O(n^2)', 'O(n)'),
        'graphs': ('Use BFS, DFS, or union-find depending on connectivity or shortest path needs.', 'O(V+E)', 'O(V+E)'),
        'greedy': ('Make the locally optimal choice at each step and prove global correctness.', 'O(n log n)', 'O(1)'),
        'heap': ('Use a priority queue to efficiently track min/max candidates.', 'O(n log n)', 'O(n)'),
        'intervals': ('Sort intervals and sweep forward, merging or selecting as needed.', 'O(n log n)', 'O(1)'),
        'linked-list': ('Use pointer manipulation or two-pointer techniques to update links in place.', 'O(n)', 'O(1)'),
        'math-bit-manipulation': ('Use arithmetic identities or bitwise operations for direct computation.', 'O(n)', 'O(1)'),
        'sliding-window': ('Maintain a window over the input and adjust boundaries to satisfy the condition.', 'O(n)', 'O(1)'),
        'stack': ('Use a stack to manage nested state or monotonic relationships.', 'O(n)', 'O(n)'),
        'trees': ('Traverse the tree and combine child results for each node.', 'O(n)', 'O(h)'),
        'trie': ('Use a prefix tree for fast prefix or wildcard search on strings.', 'O(n·k)', 'O(n·k)'),
        'two-pointers': ('Move two pointers across the input to find pairs or subarrays efficiently.', 'O(n)', 'O(1)'),
    }
    return topic_map.get(topic, ('Use the standard topic-specific pattern to solve the problem efficiently.', 'O(n)', 'O(1)'))


def generic_interview_qa(topic):
    if topic == 'dynamic-programming':
        return [
            qa('How do you identify the DP state?', 'Find overlapping subproblems and express the answer in terms of smaller results.'),
            qa('Why memoize or tabulate?', 'To avoid recomputing expensive subproblems and keep time complexity manageable.'),
        ]
    if topic == 'graphs':
        return [
            qa('When should you use BFS vs DFS?', 'Use BFS for shortest paths and layered traversal, DFS for reachability and backtracking.'),
            qa('How do you avoid revisiting nodes?', 'Mark visited nodes or use a visited set during traversal.'),
        ]
    return [
        qa('What is the key idea?', 'Choose the topic-specific pattern that best fits the problem and avoid naive brute force.'),
        qa('How do you handle edge cases?', 'Check for empty or minimal input before applying the main algorithm.'),
    ]


def build_generic_problem_data(topic, data):
    title = data.get('title', '')
    if not title:
        title = data.get('slug', '').replace('-', ' ').title()
    if not data.get('problem_statement') or 'Problem statement' in data.get('problem_statement', ''):
        data['problem_statement'] = title_to_statement(title)
    if not data.get('examples') or not isinstance(data['examples'], list) or len(data['examples']) == 0:
        data['examples'] = title_to_examples(title)
    if not data.get('constraints'):
        data['constraints'] = topic_defaults(topic)['constraints']
    if not data.get('intuition'):
        data['intuition'] = topic_defaults(topic)['intuition']
    if not data.get('approaches'):
        description, time, space = generic_approach(topic)
        data['approaches'] = [
            approach(
                'Standard Topic Approach',
                'Optimal',
                'green',
                description,
                time,
                space,
                'Brute force or naive solutions are generally too slow for interview constraints.',
                None,
            )
        ]
    if not data.get('interview_qa'):
        data['interview_qa'] = generic_interview_qa(topic)
    return data


def write_json_file(path, data):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def populate_all_questions():
    count = 0
    for topic_dir in sorted(QUESTION_DATA_DIR.iterdir()):
        if not topic_dir.is_dir():
            continue
        for json_file in sorted(topic_dir.glob('*.json')):
            with json_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
            if topic_dir.name in TOPIC_PROBLEMS:
                matches = [p for p in TOPIC_PROBLEMS[topic_dir.name] if normalize_title_to_filename(p['title']) == json_file.name]
                if matches:
                    data = matches[0]
                else:
                    data = build_generic_problem_data(topic_dir.name, data)
            else:
                data = build_generic_problem_data(topic_dir.name, data)
            write_json_file(json_file, data)
            count += 1
    return count


if __name__ == '__main__':
    total = populate_all_questions()
    print(f'Updated {total} question JSON files in all topic folders.')
