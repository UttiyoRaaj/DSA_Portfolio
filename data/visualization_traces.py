from __future__ import annotations

from typing import Any


def _workflow(current_node: str, title: str = "Execution") -> dict[str, Any]:
    return {
        "currentNode": current_node,
        "title": title,
        "nodes": [
            {"id": "setup", "label": "Start"},
            {"id": "inspect", "label": "Inspect"},
            {"id": "check", "label": "Check"},
            {"id": "store", "label": "Store"},
            {"id": "return", "label": "Return"},
        ],
        "edges": ["setup->inspect", "inspect->check", "check->store", "check->return"],
    }


def _array_structure(nums: list[int], active_indices: set[int] | None = None, visited_indices: set[int] | None = None, highlighted_indices: set[int] | None = None, answer_indices: set[int] | None = None) -> dict[str, Any]:
    active_indices = active_indices or set()
    visited_indices = visited_indices or set()
    highlighted_indices = highlighted_indices or set()
    answer_indices = answer_indices or set()
    return {
        "type": "array",
        "title": "Input Array",
        "items": [
            {
                "value": value,
                "index": index,
                "active": index in active_indices,
                "visited": index in visited_indices,
                "highlighted": index in highlighted_indices,
                "answer": index in answer_indices,
            }
            for index, value in enumerate(nums)
        ],
    }


def _hashmap_structure(entries: dict[int, int], active_key: int | None = None, highlighted_key: int | None = None) -> dict[str, Any]:
    return {
        "type": "hashmap",
        "title": "HashMap",
        "entries": [
            {
                "key": key,
                "value": value,
                "active": key == active_key,
                "highlighted": key == highlighted_key,
            }
            for key, value in entries.items()
        ],
    }


def _empty_secondary_structure() -> dict[str, Any]:
    return {
        "type": "empty",
        "title": "Other Data Structure",
        "message": "This approach only needs the input array for its walkthrough.",
    }


def _make_step(current_line: int, variables: dict[str, Any], explanation: str, workflow: dict[str, Any], main_structure: dict[str, Any], secondary_structure: dict[str, Any]) -> dict[str, Any]:
    return {
        "currentLine": current_line,
        "variables": variables,
        "mainStructure": main_structure,
        "secondaryStructure": secondary_structure,
        "dataStructures": {
            "array": main_structure if main_structure.get("type") == "array" else None,
            "hashmap": secondary_structure if secondary_structure.get("type") == "hashmap" else None,
        },
        "highlights": {"arrayIndices": []},
        "explanation": explanation,
        "workflow": workflow,
    }


def build_two_sum_trace(approach_type: str, nums: list[int] | None = None, target: int | None = None) -> list[dict[str, Any]]:
    nums = nums or [2, 7, 11, 15]
    target = target if target is not None else 9

    if approach_type == "two-sum-brute-force":
        return [
            _make_step(
                3,
                {"nums": nums, "target": target, "i": 0, "j": None, "sum": None},
                "We start with the first element and compare it with every later element.",
                _workflow("setup", "Brute force setup"),
                _array_structure(nums),
                _empty_secondary_structure(),
            ),
            _make_step(
                4,
                {"nums": nums, "target": target, "i": 0, "j": 1, "sum": nums[0] + nums[1]},
                "The second loop checks whether the pair at these positions sums to the target.",
                _workflow("inspect", "Compare a pair"),
                _array_structure(nums, active_indices={0, 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                5,
                {"nums": nums, "target": target, "i": 0, "j": 1, "sum": nums[0] + nums[1], "matches": False},
                "The sum is not the target, so the search continues with the next pair.",
                _workflow("check", "Reject this pair"),
                _array_structure(nums, active_indices={0, 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                4,
                {"nums": nums, "target": target, "i": 0, "j": 2, "sum": nums[0] + nums[2]},
                "We try the next candidate pair and check it against the target.",
                _workflow("inspect", "Try another pair"),
                _array_structure(nums, active_indices={0, 2}),
                _empty_secondary_structure(),
            ),
            _make_step(
                5,
                {"nums": nums, "target": target, "i": 0, "j": 2, "sum": nums[0] + nums[2], "matches": False},
                "This pair also misses, so the loops keep moving forward.",
                _workflow("check", "Reject again"),
                _array_structure(nums, active_indices={0, 2}),
                _empty_secondary_structure(),
            ),
            _make_step(
                4,
                {"nums": nums, "target": target, "i": 1, "j": 2, "sum": nums[1] + nums[2]},
                "We now compare the next pair and check whether it forms a solution.",
                _workflow("inspect", "Check the next candidate"),
                _array_structure(nums, active_indices={1, 2}),
                _empty_secondary_structure(),
            ),
            _make_step(
                6,
                {"nums": nums, "target": target, "i": 0, "j": 1, "sum": 9, "answer": [0, 1]},
                "The pair matches the target, so the algorithm returns those indices.",
                _workflow("return", "Return the answer"),
                _array_structure(nums, active_indices={0, 1}, answer_indices={0, 1}),
                _empty_secondary_structure(),
            ),
        ]

    if approach_type == "two-sum-two-pointers":
        sorted_pairs = sorted(((value, index) for index, value in enumerate(nums)), key=lambda item: item[0])
        return [
            _make_step(
                3,
                {"nums": nums, "target": target, "left": 0, "right": len(nums) - 1, "sortedPairs": sorted_pairs},
                "We copy the values and keep their original indices before sorting.",
                _workflow("setup", "Prepare sorted pairs"),
                _array_structure(nums, active_indices={0, len(nums) - 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                8,
                {"nums": nums, "target": target, "left": 0, "right": len(nums) - 1, "sum": sorted_pairs[0][0] + sorted_pairs[-1][0]},
                "The two-pointer scan starts from the smallest and largest values.",
                _workflow("inspect", "Set the pointer window"),
                _array_structure([entry[0] for entry in sorted_pairs], active_indices={0, len(sorted_pairs) - 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                10,
                {"nums": nums, "target": target, "left": 0, "right": len(nums) - 1, "sum": nums[0] + nums[-1]},
                "The sum is too small, so we move the left pointer to the right.",
                _workflow("check", "Move left pointer"),
                _array_structure([entry[0] for entry in sorted_pairs], active_indices={0, len(sorted_pairs) - 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                11,
                {"nums": nums, "target": target, "left": 1, "right": len(nums) - 1, "sum": nums[1] + nums[-1]},
                "We continue narrowing the search window until the pair is found.",
                _workflow("inspect", "Narrow the window"),
                _array_structure([entry[0] for entry in sorted_pairs], active_indices={1, len(sorted_pairs) - 1}),
                _empty_secondary_structure(),
            ),
            _make_step(
                13,
                {"nums": nums, "target": target, "left": 1, "right": 2, "sum": 9, "answer": [0, 1]},
                "The sum matches the target, so the algorithm returns the original indices.",
                _workflow("return", "Return the pair"),
                _array_structure([entry[0] for entry in sorted_pairs], active_indices={1, 2}, answer_indices={1, 2}),
                _empty_secondary_structure(),
            ),
        ]

    if approach_type == "two-sum-hashmap":
        map_state: dict[int, int] = {}
        steps: list[dict[str, Any]] = []

        def add_step(current_line: int, i: int | None, complement: int | None, explanation: str) -> None:
            steps.append(
                _make_step(
                    current_line,
                    {"nums": nums, "target": target, "i": i, "complement": complement, "map": {**map_state}},
                    explanation,
                    _workflow("inspect", "Walk the map"),
                    _array_structure(nums, active_indices={i} if i is not None else set()),
                    _hashmap_structure(map_state, active_key=nums[i] if i is not None else None),
                )
            )

        add_step(3, None, None, "We create an empty HashMap so we can remember values that have already been seen.")
        for i, value in enumerate(nums):
            complement = target - value
            add_step(4, i, complement, "We inspect the current element and compute the complement needed to reach the target.")
            if complement in map_state:
                add_step(5, i, complement, "The complement already exists in the map, which means we found a valid pair.")
                add_step(6, i, complement, "The algorithm returns the two indices from the HashMap and the current position.")
                break
            map_state[value] = i
            add_step(7, i, complement, "The current value is stored in the HashMap so it can be matched later.")

        return steps

    return []


def enhance_question_visualizations(question: dict[str, Any]) -> dict[str, Any]:
    for approach in question.get("approaches", []):
        visualization = approach.get("visualization")
        if not visualization:
            continue
        if visualization.get("steps"):
            continue
        approach_type = visualization.get("type")
        if not approach_type:
            continue
        visualization["steps"] = build_two_sum_trace(approach_type)
    return question
