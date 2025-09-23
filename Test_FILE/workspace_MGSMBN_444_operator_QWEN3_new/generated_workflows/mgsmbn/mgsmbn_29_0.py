# Workflow ID: mgsmbn_29_0
# Benchmark: mgsmbn
# Data Indices: [21, 123]

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

        # === PHASE 1: MULTI-PERSPECTIVE EXTRACTION (PARALLEL FORK) ===
        entity_extraction = await self.generate(
            instruction="""Extract all entities, quantities, and explicit numerical values from the Bengali problem.
            Format as:
            ENTITIES: [list of people, objects, categories]
            QUANTITIES: [value + unit + what it refers to]
            RELATIONSHIPS: [comparisons, operations, dependencies]
            GOAL: [what is being asked for]
            Be literal. Do not infer. Just extract what is stated.""",
            context=""
        )

        relational_extraction = await self.generate(
            instruction="""Focus ONLY on relationships and operations implied or stated.
            Examples: "A is twice B", "C costs $5 less than D", "after X, Y happened".
            Format as mathematical or logical expressions.
            Include temporal or causal order if present.
            Ignore entities and raw numbers — focus on connections between them.""",
            context=""
        )

        constraint_extraction = await self.generate(
            instruction="""Identify all constraints, units, and real-world boundaries.
            Examples: "must be integer", "cannot be negative", "in dollars", "per hour".
            Also extract implicit constraints: e.g., "number of people" → must be whole number.
            Format as bullet points with justification from problem text.""",
            context=""
        )

        # Merge extractions into unified problem representation
        merged_representation = await self.ensemble(
            instruction="""Synthesize the three extractions into one coherent, structured problem representation.
            Resolve conflicts by preferring interpretations that:
            - Preserve unit consistency
            - Yield integer results where expected
            - Match chronological or causal order
            - Are explicitly supported by the text
            Output format:
            [Entities]
            [Quantities with Units]
            [Relationships as Equations/Operations]
            [Constraints and Boundaries]
            [Final Goal]""",
            contexts_list=[entity_extraction, relational_extraction, constraint_extraction]
        )

        # === PHASE 2: PROBLEM CLASSIFICATION & STRATEGY SELECTION ===
        problem_classification = await self.generate(
            instruction=f"""Classify this problem based on its structure and required operations:
            Categories:
            1. SEQUENTIAL: Multiple steps in order (e.g., deposit then withdraw)
            2. PROPORTIONAL: Ratios, fractions, scaling, percentages
            3. RATE: Involves time, speed, work rate, unit price
            4. DISTRIBUTION: Sharing, dividing, remainders
            5. COMPARISON: Differences, "how many more", inequalities
            6. MULTI-ENTITY: Tracking multiple agents with different values

            Use the merged representation:
            {merged_representation}

            Output ONLY the category name and 1-sentence justification.""",
            context=merged_representation
        )

        # === PHASE 3: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN) ===
        # Generate 3 candidate solutions using different strategies
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using SEQUENTIAL strategy:
                - Break into ordered steps
                - Show intermediate results with units
                - Validate each step before proceeding
                - Final answer must be numerical only
                Problem context: {merged_representation}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC strategy:
                - Define variables for unknowns
                - Set up equations from relationships
                - Solve symbolically then numerically
                - Track units throughout
                Problem context: {merged_representation}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using DIRECT CALCULATION strategy:
                - Compute in one chain if possible
                - Prioritize efficiency
                - Explicitly state any assumptions
                - Verify against constraints
                Problem context: {merged_representation}""",
                context=""
            )
        )

        # Select best solution via ensemble
        selected_solution = await self.ensemble(
            instruction="""Select the most reliable solution based on:
            - Mathematical correctness (check arithmetic)
            - Unit consistency throughout
            - Adherence to constraints (e.g., no negative people)
            - Clarity of steps
            - Match to problem classification
            Revise selected solution to fix minor errors if needed.
            Output the full corrected solution with steps.""",
            contexts_list=solution_candidates
        )

        # === PHASE 4: ITERATIVE VERIFICATION LOOP (MAX 2 ITERATIONS) ===
        current_solution = selected_solution
        for iteration in range(2):
            verification = await self.generate(
                instruction=f"""Critically verify this solution:
                - Check each arithmetic operation
                - Confirm unit consistency at every step
                - Ensure no constraint violations (e.g., fractional people)
                - Validate final answer matches the goal
                - Flag any ambiguous or unsupported assumptions
                If errors found, describe them specifically.
                If fully correct, output "VERIFIED: [final numerical answer]".
                Solution to verify:
                {current_solution}""",
                context=current_solution
            )

            if "VERIFIED:" in verification:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following issues:
                    {verification}
                    Preserve correct parts. Only modify what's necessary.
                    Maintain step-by-step clarity and unit tracking.""",
                    context=current_solution
                )
        else:
            # If loop completes without verification, use last revision
            verification = await self.generate(
                instruction=f"""Final emergency verification. Extract numerical answer even if imperfect.
                Output format: "VERIFIED: [number]" based on best available solution.
                Solution: {current_solution}""",
                context=current_solution
            )

        # === PHASE 5: FINAL ANSWER EXTRACTION ===
        final_answer = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the verification output.
            Remove all text, units, punctuation. If decimal, preserve precision.
            If multiple numbers, select the one that answers the original question.
            Output format: single number only.""",
            context=verification
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        # If empty, return 0 as fallback
        return cleaned if cleaned else "0"