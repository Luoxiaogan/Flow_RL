# Workflow ID: mgsmbn_75_0
# Benchmark: mgsmbn
# Data Indices: [58]

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

        # PHASE 1: PROBLEM DECONSTRUCTION — Extract entities, relationships, and constraints
        deconstruction = await self.generate(
            instruction="""Perform deep semantic deconstruction of this Bengali math problem. Identify:
            1. All named entities (people, objects, places) and their associated quantities.
            2. All comparative or relational phrases (e.g., "অর্ধেক", "গুণ বেশি", "থেকে কম") and convert them into mathematical relationships (e.g., A = 0.5 * B).
            3. The explicit question being asked — what unknown must be solved for?
            4. Any implicit constraints (e.g., non-negative quantities, integer-only answers).
            5. Units of measurement and whether conversions are needed.
            Format output as a structured markdown list with clear labels for each section.""",
            context=""
        )

        # PHASE 2: STRATEGY CLASSIFICATION — Determine which solution paradigms apply
        strategy_analysis = await self.generate(
            instruction=f"""Based on the deconstructed problem structure:
            {deconstruction}

            Classify this problem into one or more of the following categories:
            - Proportional Reasoning (ratios, fractions, percentages)
            - Sequential Operations (step-by-step changes over time)
            - Multi-entity Comparison (differences, rankings, distributions)
            - Rate/Unit Problems (speed, price per unit, work rate)
            - Algebraic Unknowns (solving for variables)

            For each applicable category, explain WHY it fits and outline the core steps needed.
            Then, recommend the top 2 solution strategies to pursue in parallel.""",
            context=deconstruction
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION — Launch multiple reasoning tracks
        async def generate_algebraic_solution():
            return await self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                Given relationships: {deconstruction}
                
                Steps:
                1. Assign variables to unknown quantities (e.g., Let R = Raymond's laundry).
                2. Write equations based on extracted relationships.
                3. Solve the system of equations step by step, showing substitutions.
                4. Isolate the requested unknown.
                5. Box the final numerical answer.
                
                Emphasize symbolic manipulation over arithmetic until the final step.""",
                context=deconstruction
            )

        async def generate_arithmetic_solution():
            return await self.generate(
                instruction=f"""Solve using STEP-BY-STEP ARITHMETIC:
                Given known values: {deconstruction}
                
                Steps:
                1. Start from the given numerical anchor (e.g., Sara = 400).
                2. Apply each relationship sequentially using direct calculation.
                3. Track intermediate values explicitly (e.g., "David = Sara / 4 = 100").
                4. Compute the final requested difference or total.
                5. Box the final numerical answer.
                
                Show all intermediate arithmetic operations clearly.""",
                context=deconstruction
            )

        async def generate_unit_aware_solution():
            return await self.generate(
                instruction=f"""Solve with STRICT UNIT TRACKING:
                Given: {deconstruction}
                
                Steps:
                1. Annotate every number with its unit (e.g., 400 pounds).
                2. Verify unit consistency in every operation (e.g., multiplying pounds by scalar is valid; adding hours to pounds is invalid).
                3. Convert units only if explicitly required.
                4. Propagate units through all calculations.
                5. Final answer must include correct unit if specified, otherwise just the number.
                6. Box the final numerical answer.
                
                Reject any step that violates dimensional analysis.""",
                context=deconstruction
            )

        # Run all three solution strategies in parallel
        solution_attempts = await asyncio.gather(
            generate_algebraic_solution(),
            generate_arithmetic_solution(),
            generate_unit_aware_solution()
        )

        # PHASE 4: VALIDATION & SYNTHESIS — Cross-examine solutions
        synthesized_result = await self.ensemble(
            instruction="""You are given 3 independent solution attempts for the same Bengali math problem.
            Your task:
            1. Extract the final numerical answer from each attempt (ignore units unless specified in problem).
            2. Compare the three answers. If all match, select that answer.
            3. If they disagree, identify which solution(s) contain logical or arithmetic errors by cross-referencing with the original relationships.
            4. Prioritize solutions that correctly model the relational structure from deconstruction.
            5. Output ONLY the final agreed-upon numerical value as a single integer or decimal. No explanations.
            
            CRITICAL: If no consensus can be reached after analysis, output the arithmetic solution's answer as fallback.""",
            contexts_list=solution_attempts
        )

        # PHASE 5: CONTEXTUAL VALIDATION — Ensure answer makes real-world sense
        final_answer = await self.revise(
            instruction=f"""Validate this numerical answer against real-world constraints from the original problem:
            Original deconstruction: {deconstruction}
            Proposed answer: {synthesized_result}
            
            Checks:
            - Is the answer non-negative? (Reject if negative unless context allows)
            - Is it an integer if the problem implies discrete units (e.g., people, whole items)?
            - Does it match the scale of input values? (e.g., if inputs are ~100, answer shouldn't be ~10000)
            - Does it satisfy all stated relationships when plugged back in?
            
            If any check fails, recalculate using the arithmetic path with explicit verification.
            Otherwise, output the exact same number. NO ADDITIONAL TEXT.""",
            context=synthesized_result
        )

        # Clean and return final answer (extract only the number)
        # Use regex to extract the first number (integer or decimal) from the string
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return final_answer.strip()