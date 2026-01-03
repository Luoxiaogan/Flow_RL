# Workflow ID: mbppplus_21_0
# Benchmark: mbppplus
# Data Indices: [147, 262, 159]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: PARALLEL SEMANTIC EXTRACTION
        # Launch three concurrent deep analyses to extract orthogonal dimensions
        type_analysis, pattern_analysis, edge_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform deep input/output type analysis:
                - What are the input parameter types and structures? (e.g., string, list of integers, tuple)
                - What is the expected return type? (e.g., integer, string, boolean, list)
                - Are there any type conversion requirements?
                - What are the variable names and their semantic meanings?
                - Are there any implicit type constraints or assumptions?
                Provide structured response with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Perform algorithmic pattern recognition:
                - What category does this problem belong to? (e.g., string manipulation, array processing, mathematical computation, set operations)
                - What core algorithmic technique is required? (e.g., sorting, deduplication, regex, iteration, recursion, set comparison)
                - Are there standard library functions or modules that would be appropriate? (e.g., re, collections, itertools)
                - What is the time/space complexity requirement implied by the problem?
                - Are there any known algorithmic patterns that match this problem?
                Provide detailed analysis with examples of similar problems.""",
                context=""
            ),
            self.generate(
                instruction="""Perform edge case and boundary condition analysis:
                - What are the minimum and maximum possible input sizes?
                - What happens with empty inputs? Single element inputs?
                - Are there duplicate elements? How should they be handled?
                - Are there negative numbers, zero, or special values to consider?
                - What are the boundary conditions for loops or iterations?
                - Are there any type coercion edge cases?
                - What validation or error handling might be needed?
                List all edge cases explicitly with examples.""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE & CLASSIFY WITH CONFIDENCE SCORING
        classification = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem classification:
            1. Combine input/output type information with algorithmic pattern and edge cases.
            2. Create a comprehensive problem profile including:
               - Problem category
               - Required approach
               - Key constraints
               - Critical edge cases
               - Suggested implementation strategy
            3. Assign a confidence score from 0-100 based on consistency across analyses.
            4. If confidence < 85, explicitly state "LOW_CONFIDENCE" at the beginning.
            Format as a structured report with clear sections.""",
            contexts_list=[type_analysis, pattern_analysis, edge_analysis]
        )

        # PHASE 3: DYNAMIC SOLUTION GENERATION
        # Construct dynamic instruction based on classification
        solution = await self.generate(
            instruction=f"""Generate Python code based on this problem classification:
            {classification}
            
            Requirements:
            - Use EXACT function name and signature from original problem
            - Include all necessary imports at top of function
            - Handle ALL edge cases identified in analysis
            - Match expected return type precisely
            - Code must be efficient and readable
            - Include minimal but sufficient comments
            - Do NOT include test cases or print statements
            - Return only the function implementation as specified
            
            If classification contains "LOW_CONFIDENCE", generate two alternative approaches.
            Otherwise, generate the single best approach.""",
            context=classification
        )

        # PHASE 4: ITERATIVE REFINEMENT (up to 2 iterations)
        current_solution = solution
        for iteration in range(2):
            validation = await self.revise(
                instruction=f"""Critically review this code solution:
                - Does it handle all edge cases mentioned in the edge case analysis?
                - Is the return type exactly as required?
                - Would it pass the sample assertions shown in the problem?
                - Are there any logical errors or inefficiencies?
                - Is the code style clean and readable?
                - Are imports correct and minimal?
                
                If any issues are found, revise the code to fix them.
                If no issues, return the code unchanged.
                Maintain the exact function signature and return type.""",
                context=current_solution
            )
            
            # If no changes, break early
            if validation.strip() == current_solution.strip():
                break
            current_solution = validation

        # PHASE 5: PARALLEL FALLBACK & FINAL ENSEMBLE
        # Generate a fallback "naive" solution in parallel
        naive_solution = await self.generate(
            instruction="""Generate a simple, brute-force, obviously correct solution:
            - Don't optimize for performance
            - Focus on correctness and clarity
            - Handle edge cases explicitly
            - Use basic Python constructs (loops, conditionals)
            - Same function signature and return type
            This is a fallback in case the main solution has issues.""",
            context=""
        )

        # Final ensemble: choose between refined solution and naive fallback
        final_solution = await self.ensemble(
            instruction="""Compare these two solutions:
            1. Refined solution (potentially optimized, may be complex)
            2. Naive solution (simple, brute-force, obviously correct)
            
            Select the solution that:
            - Is most likely to be correct for all test cases
            - Handles edge cases properly
            - Matches the required return type
            - Is most readable and maintainable
            
            If both are valid, prefer the refined solution.
            Return ONLY the selected solution code, nothing else.""",
            contexts_list=[current_solution, naive_solution]
        )

        return final_solution