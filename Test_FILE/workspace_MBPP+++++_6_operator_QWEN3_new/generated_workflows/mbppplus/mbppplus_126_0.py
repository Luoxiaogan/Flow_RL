# Workflow ID: mbppplus_126_0
# Benchmark: mbppplus
# Data Indices: [261, 104]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import json

        # === PHASE 1: PARALLEL SEMANTIC EXTRACTION ===
        # Extract problem structure, constraints, and edge cases in parallel
        schema_components = await asyncio.gather(
            self.generate(
                instruction="""Analyze the problem description and infer:
                1. Input parameter types and structures (e.g., list of strings, integer n)
                2. Expected return type and format (e.g., list of tuples, sorted list)
                3. Any explicit or implicit constraints mentioned
                4. Key verbs indicating operations (e.g., 'sort', 'count', 'find common')
                Output as a structured JSON-like summary.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the algorithmic category of this problem. Choose from:
                - Frequency Analysis (word counts, most common elements)
                - Sorting/Ordering (by length, value, custom key)
                - String Parsing (regex, tokenization, pattern extraction)
                - Mathematical Computation (arithmetic, sequences, number theory)
                - Set Operations (intersection, union, difference)
                - Conditional Logic (filtering, validation, branching)
                Also identify any required Python modules (e.g., re, collections, math).
                Output as a single-line classification tag and module list.""",
                context=""
            ),
            self.generate(
                instruction="""Identify potential edge cases and boundary conditions:
                - Empty inputs (empty string, empty list, zero)
                - Single element cases
                - Duplicate elements
                - Maximum/minimum values
                - Type mismatches or unexpected formats
                - Order preservation requirements
                List each edge case with a brief rationale for why it matters.""",
                context=""
            )
        )

        # Synthesize into unified problem schema
        problem_schema = await self.ensemble(
            instruction="""Synthesize the three analyses into a single comprehensive problem schema.
            Structure as:
            {
                "input_spec": "...",
                "output_spec": "...",
                "constraints": [...],
                "algorithm_type": "...",
                "required_modules": [...],
                "edge_cases": [...]
            }
            Ensure all critical details are preserved and contradictions resolved.""",
            contexts_list=schema_components
        )

        # === PHASE 2: DYNAMIC STRATEGY ROUTING ===
        # Classify problem type to tailor code generation
        strategy_tag = await self.generate(
            instruction=f"""Based on this problem schema:
            {problem_schema}
            
            Select the optimal code generation strategy:
            A) FREQUENCY_COUNTER - for word counts, most common elements
            B) SORT_TRANSFORM - for sorting sublists, custom ordering
            C) STRING_PARSE - for regex, tokenization, text processing
            D) MATH_COMPUTE - for arithmetic, sequences, formulas
            E) GENERIC_FALLBACK - for uncategorized problems
            
            Output ONLY the single letter code (A-E).""",
            context=problem_schema
        )

        # Dynamically construct programmer instruction based on strategy
        base_instruction = f"""Generate a Python function that solves the problem according to this schema:
        {problem_schema}
        
        Requirements:
        - Use EXACT function signature from problem
        - Include necessary imports at top of function
        - Handle all edge cases identified in schema
        - Return correct data type (list, tuple, set as specified)
        - Preserve order if required
        - Be defensive against invalid inputs
        - Match reference solution's intent without copying
        
        Additional strategy-specific guidance:"""

        strategy_instructions = {
            "A": "Use collections.Counter and re.findall for word extraction. Return list of (word, count) tuples sorted by frequency then lex order.",
            "B": "Use list.sort() with appropriate key (e.g., len). Handle nested lists of varying lengths. Preserve element order within sublists.",
            "C": "Use regex patterns for text parsing. Handle punctuation, whitespace, and special characters appropriately.",
            "D": "Use mathematical operations with proper bounds checking. Handle negative numbers, zero, and floating point if applicable.",
            "E": "Implement most straightforward approach. Prioritize correctness over optimization. Include comprehensive edge case handling."
        }

        strategy_choice = strategy_tag.strip()[:1].upper()
        specific_instruction = strategy_instructions.get(strategy_choice, strategy_instructions["E"])
        full_instruction = base_instruction + "\n" + specific_instruction

        # === PHASE 3: CODE GENERATION WITH VALIDATION LOOP ===
        current_code = ""
        max_attempts = 3
        revision_attempts = 0

        for attempt in range(max_attempts):
            # Generate code
            code_result = await self.programmer(
                instruction=full_instruction,
                context=problem_schema if attempt == 0 else current_code,
                max_retries=1
            )
            
            # Extract just the code portion (assuming it's in a code block)
            code_match = re.search(r'