from __future__ import annotations

import json
import random
from datetime import datetime
from data.questions import get_topic_data
from data.chat import get_chat_messages


class TeacherAgent:
    """AI Teacher Agent for Practice Mode - teaches DSA concepts in a friendly, patient manner"""

    def __init__(self, session_id: int, selected_topics: list[str]):
        self.session_id = session_id
        self.selected_topics = selected_topics
        self.conversation_history = []
        self.current_topic = None
        self.current_concept = None
        self.teaching_progress = {}

        # Load conversation history
        self._load_conversation_history()

    def _load_conversation_history(self):
        """Load previous conversation to maintain context"""
        messages = get_chat_messages(self.session_id)
        self.conversation_history = [
            {"role": msg["role"], "content": msg["message"], "timestamp": msg["timestamp"]}
            for msg in messages
        ]
        self._infer_current_topic_from_history()

    def _infer_current_topic_from_history(self):
        """Infer the current topic from previous teacher messages."""
        for msg in reversed(self.conversation_history):
            if msg["role"] != "teacher":
                continue
            concept = self._find_concept_from_message(msg["content"].lower())
            if concept:
                self.current_topic = concept
                return

    def _get_topic_content(self, topic_slug: str) -> dict:
        """Get topic data for teaching"""
        return get_topic_data(topic_slug)

    def _find_concept_from_message(self, message: str) -> str | None:
        """Detect a concept keyword or topic slug from a message."""
        keyword_map = {
            "dynamic programming": "dynamic-programming",
            "dynamic-programming": "dynamic-programming",
            "dp": "dynamic-programming",
            "backtracking": "backtracking",
            "tree": "trees",
            "trees": "trees",
            "array": "arrays",
            "arrays": "arrays",
            "linked list": "linked-list",
            "linked-list": "linked-list",
            "stack": "stack",
            "queue": "queue",
            "hash table": "hash-table",
            "hash-table": "hash-table",
            "hash": "hash-table",
            "binary search": "binary-search",
            "binary-search": "binary-search",
            "graph": "graphs",
            "heap": "heap",
            "trie": "trie",
        }
        for phrase, slug in keyword_map.items():
            if phrase in message:
                return slug
        return None

    def _get_intuition_explanation(self, concept: str, student_level: str) -> str:
        """Explain when and why to use a concept in problem solving."""
        guides = {
            "backtracking": (
                "Backtracking is useful when you need to explore many combinations or paths and the problem asks for all valid options or one valid configuration. "
                "If you can make a choice, recurse, then undo that choice and try the next one, that's a strong hint backtracking may fit. "
                "Look for words like 'all', 'permutation', 'combination', 'subset', 'path', or 'valid arrangement' in the prompt."
            ),
            "dynamic-programming": (
                "Dynamic programming is worth considering when a problem can be broken down into overlapping subproblems and the result depends on previous computed values. "
                "If you can define the answer in terms of smaller versions of the same problem and cache those results to avoid repeated work, that's a strong signal for DP. "
                "Look for phrases like 'maximum', 'minimum', 'number of ways', 'optimal', 'longest', or 'shortest'."
            ),
            "trees": (
                "Tree-based approaches are often the right choice when the data naturally forms a hierarchy, parent-child relationships, or branching decisions. "
                "Problems involving folders, expressions, game states, or structured data usually benefit from tree thinking. "
                "If you can visualize the input as nodes connected by edges and traverse it recursively, that's a strong sign a tree solution may apply."
            ),
        }
        return guides.get(concept, f"When you see a problem that matches the structure of {concept.replace('-', ' ')}, think about how the input is organized and whether you can reuse or prune repeated work. This intuition will help you decide when to use it in a code question.")

    def _analyze_student_level(self) -> str:
        """Analyze student's current level based on conversation history"""
        if len(self.conversation_history) < 4:
            return "beginner"
        elif len(self.conversation_history) < 10:
            return "intermediate"
        else:
            return "advanced"

    def _get_friendly_greeting(self) -> str:
        """Get a friendly greeting based on time and context"""
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        greetings = [
            f"{time_greeting}! I'm excited to help you learn Data Structures and Algorithms today. I'm your friendly teacher, and I'll guide you through these concepts step by step.",
            f"{time_greeting}! Welcome to our learning session. I'm here to make DSA concepts clear and enjoyable for you. We'll take it nice and slow.",
            f"{time_greeting}! Ready to dive into some fascinating computer science concepts? I'm your patient teacher, and we'll explore these topics together.",
            f"{time_greeting}! It's wonderful to see you here. I'm committed to helping you understand these important concepts. Let's learn at your pace."
        ]
        return random.choice(greetings)

    def _explain_concept_friendly(self, concept: str, topic_data: dict, student_level: str) -> str:
        """Explain a concept in a friendly, patient manner with real-world examples"""

        explanations = {
            "beginner": {
                "arrays": "Arrays are like a row of lockers in a school hallway. Each locker has a number (that's the index), and you can store something in each one. In programming, arrays help us store multiple values of the same type together. Think of it as a shopping list where each item has a position number!",
                "linked-list": "A linked list is like a treasure hunt where each clue tells you where to find the next one. Instead of being next to each other in memory like arrays, each element points to the next. It's great when you need to add or remove items frequently, like managing a playlist where songs can be inserted anywhere.",
                "stack": "Imagine a stack of plates in a cafeteria. You can only add a plate to the top (push) or take the plate from the top (pop). This 'Last In, First Out' behavior is perfect for things like browser back buttons or undo functionality in text editors.",
                "queue": "A queue is like waiting in line at a store. The first person who arrives gets served first. This 'First In, First Out' principle is used in things like printer job queues or handling requests in web servers.",
                "hash-table": "A hash table is like a dictionary where you look up words instantly. You give it a key (like a word), and it quickly finds the associated value. It's incredibly fast for lookups, making it perfect for things like username-to-user-data mapping.",
                "binary-search": "Binary search is like finding a name in a phone book. Instead of checking every page, you open to the middle and decide whether to look left or right. This 'divide and conquer' approach is much faster than checking every item one by one.",
                "trees": "Trees are like family trees or organizational charts where each item can have children. You often traverse them recursively or level-by-level to solve problems involving hierarchies, decision paths, or nested relationships.",
                "backtracking": "Backtracking is like trying options one by one in a puzzle and undoing the last move when it doesn't lead to a solution. It helps solve problems where you explore possibilities and prune dead ends, like finding valid combinations or paths.",
                "dynamic-programming": "Dynamic programming is like solving a big problem by remembering answers to smaller subproblems so you don't repeat the same work. It's useful when the problem has overlapping subproblems and optimal substructure."
            },
            "intermediate": {
                "arrays": "Arrays provide O(1) access time to any element using indexing, but inserting/removing elements in the middle costs O(n) time. They're perfect when you know the size ahead of time and need fast random access, like implementing a simple database or image pixels.",
                "linked-list": "Linked lists excel at O(1) insertions/deletions at known positions but have O(n) access time. They're ideal for scenarios with frequent modifications, such as implementing undo functionality or managing dynamic collections where size changes often.",
                "stack": "Stacks follow LIFO principle with O(1) push/pop operations. They're fundamental in parsing expressions, implementing function call stacks, and solving problems like balanced parentheses checking or backtracking algorithms.",
                "queue": "Queues maintain FIFO order with O(1) enqueue/dequeue. They're essential for breadth-first search algorithms, task scheduling, and implementing caches with eviction policies like FIFO.",
                "hash-table": "Hash tables offer average O(1) lookup, insert, and delete operations. Collision resolution strategies like chaining or open addressing are crucial. They're used extensively in databases, caches, and symbol tables in compilers.",
                "binary-search": "Binary search requires sorted data and provides O(log n) search time. It's optimal for static datasets and forms the basis for more complex algorithms like binary search trees and database indexing.",
                "trees": "Tree algorithms often use recursion and serve well for hierarchical data, expression evaluation, and path-finding problems. Binary trees, tree traversals, and tree search strategies are common building blocks in interviews.",
                "backtracking": "Backtracking shines when you need a systematic way to explore many possible solutions and discard invalid choices quickly. It is useful in problems like permutations, combinations, graph path search, and constraint satisfaction.",
                "dynamic-programming": "Dynamic programming reduces repeated work by caching results of subproblems. It's especially useful in optimization and counting problems where the same smaller cases repeat multiple times."
            }
        }

        level = "beginner" if student_level == "beginner" else "intermediate"
        return explanations.get(level, {}).get(concept, f"Let me explain {concept} to you. This is a fundamental concept in computer science that helps us solve many real-world problems efficiently.")

    def _get_preferred_topic(self) -> str | None:
        """Return a stable topic choice from selected topics."""
        return self.selected_topics[0] if self.selected_topics else None

    def _get_teaching_suggestion(self, topic_data: dict, student_level: str) -> str:
        """Suggest what to teach next based on progress"""
        if not self.selected_topics:
            return "Let's start with the fundamentals. Which topic interests you most?"

        topic_slug = self._get_preferred_topic()
        self.current_topic = topic_slug
        topic_info = self._get_topic_content(topic_slug)

        if not topic_info:
            return "I'd love to help you learn more about Data Structures and Algorithms. What specific concept would you like me to explain?"

        topic_name = topic_info.get('title', topic_slug)
        return f"How about we explore {topic_name}? This is a really important concept that you'll use frequently in your programming career. Would you like me to explain it with some real-world examples?"

    def _get_user_intent(self, message: str) -> dict[str, bool | str | None]:
        """Classify the user's intent from their message."""
        normalized = message.lower().strip()
        return {
            "concept": self._find_concept_from_message(normalized),
            "affirmative": any(word in normalized for word in ['yes', 'sure', 'okay', 'lets', 'let\'s', 'go', 'begin', 'start', 'yep', 'yeah']),
            "negative": any(word in normalized for word in ['no', 'not', "don't", 'dont', 'never', 'confused', 'again', 'slower']),
            "ask_intuition": any(phrase in normalized for phrase in ['intuit', 'when to use', 'should i use', 'should i', 'recognize', 'identify', 'decide', 'how do i know', 'when do i know']),
            "ask_explanation": any(phrase in normalized for phrase in ['explain', 'teach me', 'tell me about', 'what is', 'what are', 'help me with', 'i want to learn', 'i want to understand', 'define', 'describe']),
            "ask_example": any(phrase in normalized for phrase in ['example', 'real world', 'practical', 'scenario', 'use case', 'illustrate', 'illustration']),
            "ask_question": any(word in normalized for word in ['why', 'how', 'when', 'what', 'which', 'should', 'could', 'would']) or normalized.endswith('?'),
        }

    def generate_response(self, user_message: str) -> str:
        """Generate a teacher response based on user input and conversation context"""

        user_message = user_message.strip()
        intent = self._get_user_intent(user_message)

        # First interaction - greeting
        if len(self.conversation_history) == 0:
            greeting = self._get_friendly_greeting()
            suggestion = self._get_teaching_suggestion(None, "beginner")
            return f"{greeting}\n\n{suggestion}"

        student_level = self._analyze_student_level()
        concept = intent["concept"]
        topic_data = self._get_topic_content(self.current_topic) if self.current_topic else None
        current_title = topic_data.get('title') if topic_data else None

        # User explicitly asks for intuition on a named concept
        if concept and intent["ask_intuition"]:
            self.current_topic = concept
            return self._get_intuition_explanation(concept, student_level)

        # User explicitly asks for an explanation of a named concept
        if concept and intent["ask_explanation"]:
            self.current_topic = concept
            topic_data = self._get_topic_content(concept)
            explanation = self._explain_concept_friendly(concept, topic_data or {}, student_level)
            return f"Sure, let's talk about {concept.replace('-', ' ')}.\n\n{explanation}\n\nDoes that help you see how and when to use it?"

        # If user asks for an example and we know the current concept/topic
        if intent["ask_example"] and self.current_topic:
            explanation = self._explain_concept_friendly(self.current_topic, self._get_topic_content(self.current_topic) or {}, student_level)
            return f"Absolutely. Here's a practical way to think about {current_title or self.current_topic}:\n\n{explanation}"

        # If user says yes/affirmative after a question or suggestion
        if intent["affirmative"] and self.current_topic:
            topic_data = self._get_topic_content(self.current_topic)
            if topic_data:
                explanation = self._explain_concept_friendly(self.current_topic, topic_data, student_level)
                return f"Great! Let's continue with {topic_data.get('title', self.current_topic)}.\n\n{explanation}\n\nDoes this make sense so far?"

        # If user mentions another concept specifically
        if concept and self.current_topic and concept != self.current_topic:
            self.current_topic = concept
            topic_data = self._get_topic_content(concept)
            explanation = self._explain_concept_friendly(concept, topic_data or {}, student_level)
            return f"Okay, let's focus on {concept.replace('-', ' ')} now.\n\n{explanation}\n\nDo you want a quick example or an intuition guide for this concept?"

        # If user asks a general question and we already have a topic in context
        if intent["ask_question"] and self.current_topic:
            topic_data = self._get_topic_content(self.current_topic)
            if topic_data:
                explanation = self._explain_concept_friendly(self.current_topic, topic_data, student_level)
                return f"Let's continue with {topic_data.get('title', self.current_topic)}.\n\n{explanation}\n\nWould you like an example or a coding pattern for this?"

        # If user is confused or asks for a different explanation style
        if intent["negative"]:
            return "No worries at all. Learning takes time, and it's completely normal to need things explained in a different way. Would you like a simpler analogy, a concrete example, or a code-oriented explanation?"

        # If user asks for another topic
        if any(word in user_message.lower() for word in ['next', 'another', 'different', 'topic', 'change']):
            if len(self.selected_topics) > 1:
                next_topic = next((t for t in self.selected_topics if t != self.current_topic), self.selected_topics[0])
                self.current_topic = next_topic
                topic_data = self._get_topic_content(self.current_topic)
                if topic_data:
                    explanation = self._explain_concept_friendly(self.current_topic, topic_data, student_level)
                    return f"Excellent. Let's explore {topic_data.get('title', self.current_topic)} next.\n\n{explanation}\n\nHow does that compare with what we discussed before?"

        # If user asks for help or wants to ask a question
        if any(word in user_message.lower() for word in ['question', 'ask', 'confused about', 'help']):
            return "Go ahead and ask your question. I can explain the idea, show you the pattern, or give you an example—whichever helps most."

        # Use current topic if possible for a helpful follow-up
        if self.current_topic:
            return f"I understand you want to continue with {current_title or self.current_topic}. Would you like a concrete example, an intuition guide, or a code pattern for this concept?"

        # If no topic is clear, ask them to be specific
        if concept:
            self.current_topic = concept
            topic_data = self._get_topic_content(concept)
            explanation = self._explain_concept_friendly(concept, topic_data or {}, student_level)
            return f"Let's focus on {concept.replace('-', ' ')}.\n\n{explanation}\n\nDoes that help you see how to use it in a problem?"

        return "I want to help you clearly understand the concept you are asking about. Could you tell me whether you want a concrete example, an intuition guide, or a code pattern?"

    def get_learning_summary(self) -> str:
        """Generate a summary of what was learned in the session"""
        if not self.conversation_history:
            return "We haven't started learning yet, but I'm excited to begin!"

        topics_discussed = set()
        for msg in self.conversation_history:
            # Simple topic detection from messages
            content = msg["content"].lower()
            for topic in self.selected_topics:
                if topic.lower() in content:
                    topics_discussed.add(topic)

        if not topics_discussed:
            return "We've been having a great conversation about Data Structures and Algorithms! Even though we haven't deep-dived into specific topics yet, you've shown great curiosity and asked thoughtful questions."

        topic_names = [get_topic_data(t).get('title', t) for t in topics_discussed]
        return f"Great session! We explored {', '.join(topic_names)}. You asked excellent questions and showed real engagement with these important concepts. Remember, consistent practice is key to mastering these topics. Feel free to continue our conversation anytime!"