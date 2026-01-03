# Workflow ID: mgsmbn_97_0
# Benchmark: mgsmbn
# Data Indices: [99]

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

        # STEP 1: PARALLEL SEMANTIC & STRUCTURAL ANALYSIS
        # Generate multiple interpretations to avoid early bias
        semantic_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of the Bengali word problem. Identify:
            - All named entities (people, objects, places)
            - All numerical values and their contextual meaning (e.g., '10 টাকা' = money, '3 ঘণ্টা' = time)
            - Verbs indicating mathematical operations (যোগ, বিয়োগ, গুণ, ভাগ, বেগ, হার, অনুপাত)
            - Question being asked (final goal)
            - Potential distractors or irrelevant information
            - Implicit constraints (e.g., non-negative quantities, integer persons)
            Output in structured bullet points.""",
            context=""
        )

        structural_analysis = await self.generate(
            instruction="""Analyze the problem structure without solving it. Determine:
            - Problem type: Rate, Distribution, Comparison, Proportional, Multi-entity, or Sequential
            - Number of distinct calculation steps required
            - Dependencies between values (what must be calculated before what)
            - Whether unit conversion is needed
            - Whether algebraic unknowns are present
            - Whether the problem is time-ordered or state-based
            Format as categorized list with clear headers.""",
            context=""
        )

        # STEP 2: ENSEMBLE TO SYNTHESIZE COHERENT PROBLEM MODEL
        problem_model = await self.ensemble(
            instruction="""Synthesize the semantic and structural analyses into a unified problem model. Resolve conflicts by:
            - Prioritizing structural categorization for solution strategy
            - Using semantic entities to ground numerical values
            - Flagging any remaining ambiguities
            - Explicitly stating what needs to be solved for
            - Listing required mathematical operations in logical order
            Output must be a single coherent paragraph followed by a bullet list of 'Steps to Solve'.""",
            contexts_list=[semantic_analysis, structural_analysis]
        )

        # STEP 3: DYNAMIC DECOMPOSITION BASED ON PROBLEM TYPE
        decomposition_instruction = f"""Decompose this problem into minimal, independent subproblems based on its type: 
        {problem_model[:500]}... [truncated for brevity]

        Guidelines:
        - Each subproblem must be solvable with one mathematical operation or unit conversion
        - Include prerequisite dependencies (e.g., 'Subproblem 2 requires Subproblem 1's result')
        - For rate problems: separate time, speed, distance calculations
        - For distribution: separate total, per-unit, remainder calculations
        - For proportional: separate ratio setup, scaling, application
        - For multi-entity: separate per-entity calculations before aggregation
        - Always include a final 'Synthesis' subproblem that combines results
        Return as list of dictionaries with 'id', 'description', 'dependencies'."""
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=problem_model
        )

        # STEP 4: PARALLEL SUBPROBLEM SOLVING WITH VALIDATION
        async def solve_subproblem(subproblem):
            # First, attempt mathematical solution
            solution_attempt = await self.programmer(
                instruction=f"""Solve this subproblem using Python:
                {subproblem['description']}
                
                Guidelines:
                - Use exact arithmetic (fractions/decimals as needed)
                - Handle unit conversions explicitly
                - Validate dimensional consistency
                - If insufficient data, return 'INSUFFICIENT_DATA'
                - Output only the numerical result or error code""",
                context=problem_model,
                max_retries=2
            )
            
            # Validate for reasonableness
            validation = await self.generate(
                instruction=f"""Validate this subproblem solution:
                Subproblem: {subproblem['description']}
                Proposed Solution: {solution_attempt}
                
                Check:
                - Does it match expected units?
                - Is it within plausible range (e.g., no negative people)?
                - Does it satisfy problem constraints?
                - Is precision appropriate (integer vs decimal)?
                Return 'VALID' or specific error message.""",
                context=problem_model
            )
            
            if "VALID" not in validation:
                # Revise with error context
                revised = await self.revise(
                    instruction=f"""Correct the solution based on validation feedback:
                    Original Attempt: {solution_attempt}
                    Validation Error: {validation}
                    Subproblem Context: {subproblem['description']}
                    Problem Model: {problem_model[:300]}...
                    Return only the corrected numerical value.""",
                    context=solution_attempt
                )
                return revised
            return solution_attempt

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in subproblems]
        )

        # Create solution mapping for synthesis
        solution_map = {sp['id']: sol for sp, sol in zip(subproblems, subproblem_solutions)}

        # STEP 5: SYNTHESIZE FINAL ANSWER
        synthesis_context = "\n".join([f"{sp['id']}: {sol}" for sp, sol in zip(subproblems, subproblem_solutions)])
        
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize the final answer using subproblem solutions:
            {synthesis_context}
            
            Steps:
            1. Identify which subproblem directly answers the main question
            2. If synthesis required, combine values as specified in decomposition
            3. Ensure final units match question requirements
            4. Round appropriately (integer if counting objects, decimal if measurements)
            5. Output ONLY the numerical value, nothing else.""",
            context=problem_model
        )

        # STEP 6: FINAL VALIDATION & EXTRACTION
        final_answer = await self.revise(
            instruction="""Extract ONLY the final numerical answer from the text below. 
            Rules:
            - Remove all units, explanations, and intermediate values
            - If multiple numbers, select the one that answers the original question
            - Ensure it's a valid number (integer or decimal)
            - If uncertain, return the most prominent number
            Output must be a single number string (e.g., '42' or '3.14')""",
            context=final_answer_draft
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        # Handle edge case where multiple dots exist
        if cleaned.count('.') > 1:
            cleaned = cleaned.replace('.', '', cleaned.count('.') - 1)
        
        return cleaned.strip()