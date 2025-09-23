# Workflow ID: mgsmbn_86_0
# Benchmark: mgsmbn
# Data Indices: [126]

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

        # === PHASE 1: PARALLEL EXTRACTION (Diamond Base) ===
        # Extract numerical, temporal, and constraint perspectives in parallel
        numerical_extraction, temporal_extraction, constraint_extraction = await asyncio.gather(
            self.generate(
                instruction="""Extract ALL numerical information with precision:
                - List every number mentioned
                - For each number, specify: 
                  * Associated entity (e.g., 'monkeys', 'gorillas')
                  * Unit of measurement (e.g., 'bananas', 'টাকা', 'hours')
                  * Temporal scope (e.g., 'per month', 'for 2 months')
                  * Mathematical relationship (e.g., 'total', 'each', 'remaining')
                - Format as bullet points with clear labels
                - Do NOT perform calculations yet
                - Flag any ambiguities or missing information""",
                context=""
            ),
            self.generate(
                instruction="""Extract temporal and logical sequence:
                - Identify all time periods mentioned (e.g., 'every 2 months', 'daily')
                - Map event sequence: what happens first, next, last?
                - Note any conditional statements ('if', 'when', 'after')
                - Identify repetition patterns (e.g., 'each month', 'per day')
                - Format as chronological steps
                - Highlight any time-based multipliers or divisors""",
                context=""
            ),
            self.generate(
                instruction="""Extract constraints and real-world boundaries:
                - Identify physical constraints (e.g., 'cannot be negative', 'must be integer')
                - Note unit consistency requirements (e.g., 'convert hours to minutes')
                - Flag any implicit assumptions (e.g., 'assume constant rate')
                - Identify boundary conditions (e.g., 'minimum', 'maximum', 'remainder')
                - Format as constraint list with justification
                - Highlight any potential contradictions in the problem""",
                context=""
            )
        )

        # === PHASE 2: PARALLEL SOLUTION ATTEMPTS ===
        # Each extraction feeds a specialized solver
        numerical_solution, temporal_solution, constraint_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Using ONLY the numerical data below, compute the answer:
                {numerical_extraction}
                
                Steps:
                1. Identify the target quantity (what are we solving for?)
                2. Map relationships between numbers (add? multiply? divide?)
                3. Perform step-by-step arithmetic with intermediate results
                4. Apply unit conversions if needed
                5. State final answer clearly
                
                Show ALL work. Do NOT consider time or constraints yet.""",
                context=numerical_extraction
            ),
            self.generate(
                instruction=f"""Using ONLY the temporal sequence below, compute the answer:
                {temporal_extraction}
                
                Steps:
                1. Build timeline of events
                2. Identify scaling factors (e.g., 'for 2 months' means multiply by 2)
                3. Apply operations in chronological order
                4. Track cumulative totals
                5. State final answer clearly
                
                Show ALL work. Do NOT consider constraints or raw numbers yet.""",
                context=temporal_extraction
            ),
            self.generate(
                instruction=f"""Using ONLY the constraints below, compute the answer:
                {constraint_extraction}
                
                Steps:
                1. Identify how constraints affect calculations
                2. Adjust for boundaries (rounding, flooring, etc.)
                3. Verify unit consistency
                4. Apply constraint-aware arithmetic
                5. State final answer clearly
                
                Show ALL work. Do NOT consider raw numbers or timing yet.""",
                context=constraint_extraction
            )
        )

        # === PHASE 3: ENSEMBLE SYNTHESIS WITH CONFLICT RESOLUTION ===
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution attempts below into one correct answer:
            - Compare all three solutions
            - Identify points of agreement and disagreement
            - For disagreements: determine root cause (e.g., missed multiplier, unit error)
            - Apply constraint validation to resolve conflicts
            - Reconcile temporal scaling with numerical totals
            - Produce single coherent solution with step-by-step justification
            - Final answer must satisfy ALL perspectives
            
            Format:
            CONFLICT ANALYSIS: [explain discrepancies]
            RESOLUTION STRATEGY: [how you fixed them]
            FINAL SOLUTION: [step-by-step with answer]""",
            contexts_list=[numerical_solution, temporal_solution, constraint_solution]
        )

        # === PHASE 4: VALIDATION & ITERATIVE REFINEMENT ===
        validation = await self.generate(
            instruction=f"""Validate the solution against the original problem:
            - Does the answer satisfy all stated conditions?
            - Are all entities accounted for?
            - Is the temporal scope correctly applied?
            - Are constraints respected?
            - Is the unit correct?
            - Would this answer make sense to a 5th grader?
            
            Respond ONLY with:
            VALID if perfect
            INVALID: [specific reason] if flawed""",
            context=synthesized_solution
        )

        final_solution = synthesized_solution
        if "INVALID" in validation:
            # Targeted revision based on validation feedback
            final_solution = await self.revise(
                instruction=f"""Revise the solution based on this validation feedback:
                {validation}
                
                Steps:
                1. Identify which extraction phase failed (numerical/temporal/constraint)
                2. Re-extract ONLY that component with focused attention
                3. Recompute affected calculations
                4. Re-validate against original problem
                5. Output corrected solution with clear explanation of fix
                
                Preserve correct parts of original solution.""",
                context=synthesized_solution
            )

        # === PHASE 5: ANSWER EXTRACTION ===
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below.
            - Must be a single number (integer or decimal)
            - Remove all units, explanations, and text
            - If multiple numbers, pick the one that answers the main question
            - If no clear number, return 0
            
            Example outputs: "1400", "3.14", "0" """,
            context=final_solution
        )

        # Clean and return answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned_answer if cleaned_answer else "0"