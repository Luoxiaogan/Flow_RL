# Workflow ID: mbppplus_59_0
# Benchmark: mbppplus
# Data Indices: [159, 207]

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
        import json

        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Output a JSON-like classification with these keys:
            - "problem_type": One of ["decision_function", "transformation", "search", "validation", "computation"]
            - "input_type": The primary input data structure (e.g., "list", "tuple", "string", "set")
            - "output_type": The expected return type (e.g., "bool", "str", "int", "list")
            - "core_operation": The fundamental algorithmic operation (e.g., "membership_test", "uniqueness_check", "sorting", "filtering")
            - "edge_cases": List of edge cases to handle (e.g., ["empty_input", "single_element", "duplicates", "boundary_values"])
            - "constraints": Any explicit or implicit constraints (e.g., "in_place", "no_extra_space", "preserve_order")
            - "complexity_target": If mentioned, the expected time/space complexity; otherwise "not_specified"
            
            Base your analysis solely on the problem description and function signature. Be precise and exhaustive.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_instructions = [
            """Based on the problem classification, propose Strategy A: The most straightforward, readable approach.
            - Describe the algorithm in pseudocode
            - Analyze time and space complexity
            - List which edge cases it handles naturally and which require explicit checks
            - Note any Python-specific optimizations or idioms that apply""",
            
            """Based on the problem classification, propose Strategy B: The most efficient approach (time or space optimized).
            - Describe the algorithm in pseudocode
            - Analyze time and space complexity
            - Explain trade-offs between readability and performance
            - Note any preprocessing or data structure transformations required""",
            
            """Based on the problem classification, propose Strategy C: The most robust/defensive approach.
            - Describe the algorithm in pseudocode
            - Focus on comprehensive edge case handling and input validation
            - Include explicit checks for all edge cases mentioned in classification
            - Consider type safety and error handling even if not explicitly required"""
        ]

        strategy_tasks = [
            self.generate(instruction=instr, context=classification)
            for instr in strategy_instructions
        ]
        strategies = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Selection via Ensemble
        selected_strategy = await self.ensemble(
            instruction="""You are a senior software architect selecting the optimal implementation strategy. Consider:
            1. CORRECTNESS: Must handle all edge cases listed in the classification
            2. EFFICIENCY: Should meet or exceed any complexity targets
            3. READABILITY: Code should be clean and maintainable
            4. PYTHONIC: Should follow Python best practices and idioms
            5. ROBUSTNESS: Should include necessary guards against edge cases
            
            Evaluate each strategy against these criteria. Select the single best strategy and justify your choice in 3-5 sentences.
            Then, output a SPECIFICATION for the programmer that includes:
            - Exact algorithm to implement (with step-by-step instructions)
            - Required edge case handlers (as bullet points)
            - Expected input/output types and any type conversion rules
            - Variable naming conventions to follow
            - Any specific Python constructs or built-ins to use or avoid""",
            contexts_list=strategies
        )

        # Phase 4: Code Generation
        initial_code = await self.programmer(
            instruction="""Generate a complete, production-ready Python function that solves the problem exactly as specified.
            Requirements:
            - Use the EXACT function signature from the problem
            - Implement the algorithm specified in the strategy selection
            - Handle ALL edge cases mentioned in the specification
            - Include type-appropriate returns (e.g., don't return list when tuple expected)
            - Use clear, descriptive variable names following the naming conventions specified
            - No unnecessary comments or print statements
            - Code must be PEP8 compliant
            - Do NOT include test cases or example usage
            
            The solution must be robust enough to pass extensive hidden test suites including edge cases.""",
            context=selected_strategy
        )

        # Phase 5: Code Revision and Quality Assurance
        final_code = await self.revise(
            instruction="""You are a code reviewer performing a strict quality audit. Check the code for:
            1. TYPE CONSISTENCY: Verify input/output types match problem requirements
            2. EDGE CASE COVERAGE: Ensure all edge cases from classification are handled
            3. ALGORITHMIC CORRECTNESS: Verify logic matches the selected strategy
            4. PYTHON BEST PRACTICES: Check for PEP8, appropriate built-ins, and idiomatic Python
            5. EFFICIENCY: No obvious performance anti-patterns
            6. ROBUSTNESS: No unhandled exceptions or assumptions about input validity
            
            If any issues are found, rewrite the ENTIRE function with corrections. If no issues, return the original code unchanged.
            Preserve the exact function signature and return type requirements.""",
            context=initial_code
        )

        return final_code