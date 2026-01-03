# Workflow ID: limr_18_0
# Benchmark: limr
# Data Indices: [34, 294]

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

        # STEP 1: Problem Typing and Strategic Framing
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your analysis must include:
            1. Primary mathematical domain(s): Is this geometry, algebra, combinatorics, number theory, calculus, or probability? Assign primary and secondary domains if mixed.
            2. Key entities: Identify all variables, functions, constraints, and unknowns. Specify their mathematical nature (e.g., integer, real, function, set).
            3. Solution paradigms: List 2-3 potential high-level strategies to solve this (e.g., "coordinate geometry approach", "generating functions", "modular arithmetic reduction").
            4. Expected answer format: Confirm the answer is an integer 000-999. Note any constraints (e.g., positive, even, prime).
            5. Complexity indicators: Estimate the number of non-trivial steps required and flag any potential traps (e.g., "requires casework", "easy to misread transformation").
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # STEP 2: Dynamic Decomposition
        decomposition = await self.decompose(
            instruction=f"""Based on the following problem analysis:
            {problem_analysis}
            
            Decompose this problem into a sequence of logically dependent subproblems. Each subproblem should be:
            - Atomic: Solvable as a single conceptual step
            - Ordered: Dependencies must reflect mathematical necessity (e.g., "solve for x before computing x+y")
            - Annotated: Include the mathematical technique required (e.g., "polynomial factorization", "vector dot product")
            - Pruned: Avoid trivial steps (e.g., "copy equation") unless critical for validation
            
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=problem_analysis
        )

        # STEP 3: Parallel Strategy Exploration
        # For each top-level approach hinted in problem_analysis, generate a solution path
        strategy_prompts = [
            """Solve the problem using an ALGEBRAIC approach. Focus on:
            - Symbolic manipulation
            - Equation setup and solving
            - Function transformations
            - Avoid numerical methods unless necessary
            Show all steps clearly and justify each transformation.""",
            
            """Solve the problem using a GEOMETRIC/VISUAL approach. Focus on:
            - Coordinate systems and transformations
            - Graph properties and symmetries
            - Intersection and distance calculations
            - Diagram-based reasoning if applicable
            Translate visual insights into algebraic expressions.""",
            
            """Solve the problem using a COMPUTATIONAL/ENUMERATIVE approach. Focus on:
            - Case analysis and exhaustive search (if bounded)
            - Algorithmic thinking
            - Pattern recognition in sequences or structures
            - Modular or recursive decomposition
            Prioritize efficiency and mathematical insight over brute force."""
        ]

        # Launch parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=prompt, context=problem_analysis) for prompt in strategy_prompts]
        )

        # STEP 4: Code-Assisted Validation for Each Attempt
        validation_tasks = []
        for i, attempt in enumerate(solution_attempts):
            validation_task = self.programmer(
                instruction=f"""Validate the following mathematical solution attempt:
                {attempt}
                
                Your task:
                1. Extract all numerical claims and algebraic assertions.
                2. Implement computational checks for each claim (e.g., verify intersection points, check divisibility, validate recursive formulas).
                3. Flag any inconsistencies, calculation errors, or logical gaps.
                4. Return "VALID" if all checks pass, "INVALID: [reason]" if any fail.
                5. If validation is impossible (e.g., purely theoretical proof), return "UNVERIFIABLE" with explanation.
                
                Be rigorous. Do not assume correctness. Test edge cases implied by the problem.""",
                context=attempt
            )
            validation_tasks.append(validation_task)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # STEP 5: Ensemble Synthesis with Confidence Scoring
        synthesis_input = [
            f"""SOLUTION ATTEMPT {i+1}:
            {attempt}
            
            VALIDATION: {validation}
            """ 
            for i, (attempt, validation) in enumerate(zip(solution_attempts, validation_results))
        ]

        synthesized_solution = await self.ensemble(
            instruction="""You are a senior mathematics competition judge. Your task:
            1. Compare all solution attempts and their validation results.
            2. Assign a confidence score (0-100) to each based on:
               - Internal logical consistency
               - Validation success (VALID > UNVERIFIABLE > INVALID)
               - Elegance and minimality of steps
               - Alignment with problem constraints
            3. If all high-confidence (>80) solutions agree on an answer, select it.
            4. If there is disagreement or low confidence, identify the core conflict and propose a SYNTHESIZED SOLUTION that resolves it.
            5. Output ONLY the final chosen solution with clear justification and the integer answer.
            
            CRITICAL: The final answer must be an integer between 000 and 999. Extract it explicitly.""",
            contexts_list=synthesis_input
        )

        # STEP 6: Meta-Validation Loop (Adaptive Depth)
        # Check for low confidence or conflict
        needs_refinement = await self.generate(
            instruction=f"""Analyze this synthesized solution:
            {synthesized_solution}
            
            Return "REFINE" if:
            - Confidence score is below 80
            - Multiple conflicting answers were present
            - Validation results showed major inconsistencies
            - The solution path seems incomplete or hand-wavy
            
            Return "ACCEPT" if the solution is rigorous, validated, and unambiguous.
            
            Respond ONLY with "REFINE" or "ACCEPT".""",
            context=synthesized_solution
        )

        final_solution = synthesized_solution
        if "REFINE" in needs_refinement.upper():
            # Launch meta-analysis and re-solve
            conflict_analysis = await self.generate(
                instruction=f"""The following solutions and validations showed conflicts or low confidence:
                {json.dumps(synthesis_input, indent=2)}
                
                Perform a root-cause analysis:
                1. What fundamental assumption or step caused divergence?
                2. Which mathematical principle was misapplied?
                3. Propose a NEW solution strategy that avoids these pitfalls.
                4. Outline the corrected step-by-step approach.
                
                Be brutally honest. Focus on mathematical truth, not saving face.""",
                context=""
            )
            
            # Generate new solution based on conflict analysis
            refined_solution = await self.generate(
                instruction=f"""Using this conflict analysis:
                {conflict_analysis}
                
                Generate a CORRECTED, RIGOROUS solution to the original problem. This is your final attempt.
                - Address all identified flaws
                - Include more detailed verification steps
                - Ensure every claim is justified
                - Extract the final integer answer (000-999) explicitly at the end""",
                context=conflict_analysis
            )
            
            final_solution = refined_solution

        # STEP 7: Final Answer Extraction and Formatting
        boxed_answer = await self.revise(
            instruction="""Extract the final numerical answer from the solution below. Rules:
            1. The answer MUST be an integer between 000 and 999.
            2. If multiple candidates exist, choose the one with strongest validation.
            3. Format STRICTLY as \boxed{XYZ} where XYZ is the 3-digit number (pad with leading zeros if needed).
            4. If no valid answer is found, return \boxed{000} as fallback.
            
            DO NOT include any other text or explanation. Only the boxed answer.""",
            context=final_solution
        )

        return boxed_answer