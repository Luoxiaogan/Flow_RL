# Workflow ID: mgsmbn_49_0
# Benchmark: mgsmbn
# Data Indices: [53, 67]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Break problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify:
            1. All entities (people, objects, places) and their roles
            2. All numerical values and what they quantify (include units like টাকা, টুকরো, etc.)
            3. All mathematical relationships (ratios, sums, differences, products, fractions)
            4. The unknown(s) we need to solve for
            5. Any implicit constraints (non-negative, integer-only, real-world plausibility)
            6. Dependencies between subproblems (what must be solved first)
            
            Structure output as a dependency graph of subproblems. Each subproblem should be self-contained and solvable with basic arithmetic.
            Prioritize chronological or causal ordering when applicable.""",
            context=""
        )

        # STEP 2: PARALLEL INTERPRETATION GENERATION - Handle ambiguity
        interpretation_instructions = [
            """Generate a literal interpretation: Translate the Bengali problem directly into mathematical expressions without inferring hidden relationships. Focus on explicit numbers and operations mentioned.""",
            """Generate a proportional interpretation: Identify any ratios, percentages, or multiplicative relationships that may be implied (e.g., '10 গুণ বেশি' as 10x multiplier). Model as equations.""",
            """Generate a unit-consistency interpretation: Track all units (টাকা, ঘণ্টা, জিনিস) and ensure dimensional analysis is maintained throughout. Convert units if necessary before calculation."""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instruction=instr, context=json.dumps(decomposition)) 
              for instr in interpretation_instructions]
        )

        # STEP 3: PARALLEL VALIDATION - Execute code for each interpretation
        validation_tasks = []
        for i, interpretation in enumerate(interpretations):
            task = self.programmer(
                instruction=f"""Generate and execute Python code to solve the problem based on this interpretation:
                {interpretation}
                
                Requirements:
                - Use only basic arithmetic operations (+, -, *, /)
                - Maintain unit consistency (convert if needed)
                - Validate that result is non-negative and contextually plausible
                - If multiple unknowns, solve system of equations
                - Return ONLY the numerical answer (no text)
                
                If code fails or produces implausible result, throw an exception.""",
                context=interpretation,
                max_retries=1
            )
            validation_tasks.append(task)

        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)

        # Filter out failed validations
        successful_solutions = []
        for i, result in enumerate(validation_results):
            if not isinstance(result, Exception) and result.strip().replace('.','',1).isdigit():
                successful_solutions.append(result.strip())

        # STEP 4: ENSEMBLE SELECTION - Choose best solution
        if len(successful_solutions) == 0:
            # Fallback: Direct programmer attempt with decomposition context
            final_answer = await self.programmer(
                instruction="""Solve the problem directly using the decomposition structure. 
                Extract entities, relationships, and constraints from the decomposition.
                Generate Python code that:
                - Models all identified relationships
                - Respects all constraints
                - Computes the unknown
                - Returns ONLY the numerical answer""",
                context=json.dumps(decomposition),
                max_retries=3
            )
        elif len(successful_solutions) == 1:
            final_answer = successful_solutions[0]
        else:
            # Multiple valid solutions - ensemble to select best
            final_answer = await self.ensemble(
                instruction="""Select the best numerical answer based on:
                1. Consistency with original problem text (check against self.problem_text)
                2. Mathematical soundness (no division by zero, no negative quantities where impossible)
                3. Unit consistency (answer should match expected unit type)
                4. Simplicity (prefer integer over decimal if inputs are integers)
                5. Real-world plausibility
                
                Return ONLY the selected numerical answer.""",
                contexts_list=successful_solutions
            )

        # STEP 5: ITERATIVE REFINEMENT - Verify and revise if needed
        for _ in range(2):  # Up to 2 refinement cycles
            verification = await self.generate(
                instruction=f"""Verify this solution against the original problem:
                Proposed Answer: {final_answer}
                
                Check:
                1. Does it satisfy all explicit conditions?
                2. Are all quantities accounted for?
                3. Are units consistent throughout?
                4. Is the answer format correct (single numerical value)?
                5. Any arithmetic errors in derivation?
                
                If any issues found, describe them specifically. Otherwise, respond 'VERIFIED'.""",
                context=final_answer
            )

            if "VERIFIED" in verification.upper():
                break
            else:
                # Revise based on verification feedback
                final_answer = await self.revise(
                    instruction=f"""Revise the solution based on this feedback:
                    {verification}
                    
                    Requirements:
                    - Fix identified errors
                    - Maintain mathematical correctness
                    - Preserve unit consistency
                    - Return ONLY the numerical answer""",
                    context=final_answer
                )

        return final_answer.strip()