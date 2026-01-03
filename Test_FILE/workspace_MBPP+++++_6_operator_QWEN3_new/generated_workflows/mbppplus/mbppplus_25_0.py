# Workflow ID: mbppplus_25_0
# Benchmark: mbppplus
# Data Indices: [189, 91]

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

        # Phase 1: Problem Decomposition & Parallel Analysis
        decomposition = await self.decompose(
            instruction="""Break this programming problem into atomic subproblems. For each:
            1. Identify core computational/mathematical operation needed
            2. List required input/output types and constraints
            3. Note any ambiguous terms needing disambiguation
            4. Flag potential edge cases (empty, zero, negative, overflow, type mismatches)
            Return as numbered subproblems with dependencies if any.""",
            context=""
        )

        # Run parallel analyses: structure, edge cases, output format
        structure_analysis, edge_case_analysis, format_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the mathematical or logical structure of this problem.
                - What invariant or pattern must hold?
                - Is this a transformation, validation, or computation task?
                - What known algorithms or patterns apply?
                - Express core logic in pseudocode or mathematical notation.""",
                context=""
            ),
            self.generate(
                instruction="""Systematically enumerate ALL plausible edge cases, including:
                - Empty inputs (lists, strings, sets)
                - Single-element inputs
                - Zero, negative, or extreme values
                - Type mismatches or invalid inputs
                - Boundary conditions (max/min values, overflow)
                - Duplicates or repeated elements
                Format as bullet points with brief rationale for each.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze output format requirements:
                - Exact return type (list, tuple, set, int, bool, etc.)
                - Order sensitivity (does order matter?)
                - Precision requirements (floating point, modular arithmetic)
                - Error handling expectations (raise exception or return sentinel?)
                Extract explicit and implicit format constraints from problem text.""",
                context=""
            )
        )

        # Phase 2: Context Distillation & Validation
        distilled_context = await asyncio.gather(
            self.summarize(
                instruction="Extract key mathematical structure and core logic. Keep only essential pseudocode and invariants.",
                context=structure_analysis
            ),
            self.summarize(
                instruction="Condense edge cases into minimal test suite. Prioritize by likelihood and severity.",
                context=edge_case_analysis
            ),
            self.summarize(
                instruction="Extract exact output format specifications. List type, structure, and constraints.",
                context=format_analysis
            )
        )

        # Combine distilled insights
        combined_context = "\n\n".join([
            "STRUCTURE: " + distilled_context[0],
            "EDGE CASES: " + distilled_context[1],
            "FORMAT: " + distilled_context[2]
        ])

        # Phase 3: Solution Drafting & Refinement
        solution_draft = await self.generate(
            instruction=f"""Generate a complete Python function solution using this context:
            {combined_context}
            
            Requirements:
            - Match exact function signature from problem
            - Handle all edge cases listed above
            - Adhere strictly to output format
            - Include minimal necessary imports
            - No type hints or docstrings unless specified
            - Return correct data type (list vs tuple vs set matters)
            - For mathematical problems, consider modular arithmetic or overflow
            - For list problems, consider index bounds and mutability""",
            context=combined_context
        )

        # Phase 4: Iterative Refinement (max 2 rounds)
        refined_solution = solution_draft
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically review this code:
                {refined_solution}
                
                Check:
                1. Does it handle ALL edge cases from context?
                2. Does output type/format exactly match requirements?
                3. Are there off-by-one errors or index issues?
                4. Is logic mathematically sound?
                5. Any unhandled exceptions or type errors?
                Return specific line-by-line fixes needed.""",
                context=refined_solution
            )
            
            if "no issues" in validation.lower() or "correct" in validation.lower():
                break
                
            refined_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                {validation}
                
                Preserve function signature and core logic.
                Only change what's necessary to fix identified problems.
                Maintain clean, readable code.""",
                context=refined_solution
            )

        # Phase 5: Final Code Generation & Synthesis
        final_code_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Implement final solution with this context:
                {combined_context}
                
                Requirements:
                - Generate ONLY the function implementation
                - Use EXACT function name from problem
                - Include necessary imports at top
                - Preserve parameter names
                - Return correct data type
                - Handle edge cases explicitly
                - No wrapper functions or classes
                - Code must be production-ready and pass all tests""",
                context=refined_solution,
                max_retries=3
            ),
            # Alternative approach: direct from distilled context
            self.programmer(
                instruction=f"""Alternative implementation based on core structure:
                {distilled_context[0]}
                
                Ignore previous code. Generate fresh solution focusing on:
                - Mathematical correctness
                - Edge case robustness
                - Minimalist implementation
                Follow all format requirements strictly.""",
                context=combined_context,
                max_retries=3
            )
        )

        # Ensemble: Select best or merge insights
        final_code = await self.ensemble(
            instruction="""Select the most robust solution:
            - Prefer solutions that explicitly handle edge cases
            - Choose code with clearest logic and fewest assumptions
            - Ensure output format matches exactly
            - If both are valid, pick more efficient or elegant version
            - If neither is perfect, synthesize a hybrid solution
            Return ONLY the final code block with imports and function.""",
            contexts_list=final_code_attempts
        )

        # Extract just the code block (remove any explanatory text)
        code_match = re.search(r'