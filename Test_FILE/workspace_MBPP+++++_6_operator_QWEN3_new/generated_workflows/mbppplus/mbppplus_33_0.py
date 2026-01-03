# Workflow ID: mbppplus_33_0
# Benchmark: mbppplus
# Data Indices: [288, 315]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
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
        """
        Universal workflow for programming problem-solving domain.
        Adapts strategy based on problem classification, handles edge cases,
        and iteratively refines code for correctness and robustness.
        """
        import asyncio
        import re

        # === PHASE 1: PARALLEL CLASSIFICATION ===
        classification_instructions = [
            """Analyze the problem from an ALGORITHMIC perspective:
            - What category of algorithm is needed? (e.g., search, sort, transform, math)
            - What is the core computational task?
            - Are there obvious brute-force vs optimized approaches?
            - What data structures are involved?
            Provide a structured classification with clear labels.""",
            
            """Analyze the problem from a STRUCTURAL perspective:
            - What are the input and output types? (list, tuple, set, etc.)
            - Are there constraints on order, duplicates, or mutability?
            - What edge cases are likely? (empty, single element, boundary values)
            - How should the solution handle type consistency?
            Provide a detailed structural breakdown.""",
            
            """Analyze the problem from a MATHEMATICAL/LOGICAL perspective:
            - Is this a combinatorial, arithmetic, or logical problem?
            - Are there invariants or mathematical properties to exploit?
            - What are the success/failure conditions?
            - Can the problem be reduced to a known pattern?
            Provide a mathematical/logical characterization."""
        ]

        # Generate 3 parallel classifications
        classifications = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in classification_instructions]
        )

        # === PHASE 2: CONSENSUS BUILDING ===
        problem_strategy = await self.ensemble(
            instruction="""Synthesize the three classifications into a unified problem understanding:
            - Identify the dominant problem type (transformation, search, math, etc.)
            - Extract key constraints and edge cases mentioned across all analyses
            - Determine the recommended solution approach (brute force, optimized, hybrid)
            - Note any conflicts between classifications and resolve them
            Output a concise, actionable strategy summary.""",
            contexts_list=classifications
        )

        # === PHASE 3: CONSTRAINT EXTRACTION ===
        constraints = await self.generate(
            instruction=f"""Based on the unified strategy:
            {problem_strategy}
            
            Extract and list ALL constraints and requirements:
            - Input types and structures
            - Output types and structures (MUST match exactly)
            - Edge cases to handle (empty, single, duplicates, negatives, etc.)
            - Performance or efficiency requirements
            - Any implicit assumptions from the problem context
            Format as a bulleted list with clear, unambiguous statements.""",
            context=problem_strategy
        )

        # === PHASE 4: DYNAMIC SPEC SYNTHESIS ===
        programming_spec = await self.generate(
            instruction=f"""Create a detailed programming specification:
            PROBLEM STRATEGY:
            {problem_strategy}
            
            CONSTRAINTS:
            {constraints}
            
            SPEC REQUIREMENTS:
            - MUST output ONLY the function implementation (no explanations, no markdown)
            - Function signature MUST match exactly what's implied by the problem
            - Include necessary imports INSIDE the function if needed
            - Handle ALL edge cases listed in constraints
            - Ensure type consistency (return tuple if expected, list if expected, etc.)
            - Prioritize correctness over performance unless specified otherwise
            - Code must be self-contained and immediately executable
            
            Generate the most robust, edge-case-aware implementation possible.
            """,
            context=f"{problem_strategy}\n\n{constraints}"
        )

        # === PHASE 5: CODE GENERATION & ITERATIVE REFINEMENT ===
        current_code = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            if attempt == 0:
                # First attempt: generate from spec
                code_result = await self.programmer(
                    instruction=f"""Implement the solution according to this spec:
                    {programming_spec}
                    
                    CRITICAL: Output ONLY the function implementation. No additional text.
                    Include imports inside the function if needed.
                    Handle all edge cases and type requirements specified.""",
                    context=programming_spec
                )
            else:
                # Subsequent attempts: revise based on critique
                critique = await self.generate(
                    instruction=f"""Critique this code for robustness and correctness:
                    {current_code}
                    
                    Focus on:
                    - Edge case handling (empty inputs, single elements, duplicates, etc.)
                    - Type consistency (returning correct data types)
                    - Logic errors or off-by-one mistakes
                    - Performance issues if any
                    - Compliance with original problem constraints
                    
                    Provide specific, actionable feedback for improvement.""",
                    context=current_code
                )
                
                code_result = await self.revise(
                    instruction=f"""Revise the code based on this critique:
                    {critique}
                    
                    CRITICAL REQUIREMENTS:
                    - Output ONLY the function implementation (no explanations)
                    - Preserve the exact function signature
                    - Include imports inside function if needed
                    - Fix all identified issues while maintaining core logic
                    - Ensure edge case robustness""",
                    context=current_code
                )
            
            # Extract just the code portion (in case programmer adds explanatory text)
            # Look for def keyword and extract until end of function
            code_match = re.search(r'(def\s+\w+.*?:.*?)(?=\n\s*(?:def|\Z))', code_result, re.DOTALL)
            if code_match:
                current_code = code_match.group(1).strip()
            else:
                current_code = code_result.strip()
            
            # If this is the last attempt or code looks reasonable, break
            if attempt == max_retries - 1 or len(current_code) > 50:  # Simple heuristic
                break

        return current_code