# Workflow ID: mgsmbn_40_0
# Benchmark: mgsmbn
# Data Indices: [177, 141]

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

        # === PHASE 1: MULTI-PERSPECTIVE PROBLEM DECOMPOSITION ===
        # Extract core components through three parallel analytical lenses
        math_lens, narrative_lens, constraint_lens = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem purely from a mathematical perspective. Ignore narrative context. Extract:
                - All numerical values and their symbolic roles (e.g., 'rate', 'quantity', 'total')
                - Required operations (add, multiply, convert units, etc.)
                - Unknown variable to solve for
                - Mathematical relationships (equations, proportions, sequences)
                Format as structured bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Reconstruct the problem as a chronological narrative. Identify:
                - Sequence of events or actions
                - Actors (people/objects) and their roles
                - Temporal or causal dependencies
                - Implicit steps not explicitly stated
                Present as a timeline with numbered steps, preserving original Bengali context where critical.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all units, constraints, and real-world boundaries:
                - Physical units (minutes, seconds, টাকা, জিনিস) and required conversions
                - Constraints (non-negative, integer-only, fractional allowances)
                - Ambiguities or missing information needing assumptions
                - Plausibility checks (e.g., 'Can time be negative?')
                Format as categorized list with explicit flags for critical issues.""",
                context=""
            )
        )

        # === PHASE 2: SYNTHESIZE UNIFIED PROBLEM MODEL ===
        problem_model = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, coherent problem specification. Resolve conflicts by:
            1. Prioritizing mathematical consistency
            2. Then ensuring unit coherence
            3. Then aligning with narrative plausibility
            Output must include exactly:
            [KNOWN_VALUES]: Structured list with units and roles
            [UNKNOWN]: Clearly stated target variable
            [OPERATION_SEQUENCE]: Ordered steps with unit conversions
            [VALIDATION_CHECKS]: Constraints and plausibility rules
            Format precisely with these section headers.""",
            contexts_list=[math_lens, narrative_lens, constraint_lens]
        )

        # === PHASE 3: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL ===
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using this problem model:
                {problem_model}

                Generate Solution Strategy A: Compute by activity type first (e.g., all crosswords, then all sudoku). Show:
                - Step-by-step arithmetic with intermediate results
                - Explicit unit conversions at each step
                - Final answer boxed at end""",
                context=problem_model
            ),
            self.generate(
                instruction=f"""Using this problem model:
                {problem_model}

                Generate Solution Strategy B: Compute per-item time first, then scale by quantity. Show:
                - Step-by-step arithmetic with intermediate results
                - Explicit unit conversions at each step
                - Final answer boxed at end""",
                context=problem_model
            ),
            self.generate(
                instruction=f"""Using this problem model:
                {problem_model}

                Generate Solution Strategy C: Convert all units to smallest denomination first (e.g., seconds), then compute. Show:
                - Step-by-step arithmetic with intermediate results
                - Explicit unit conversions at each step
                - Final answer boxed at end""",
                context=problem_model
            )
        )

        # === PHASE 4: VALIDATE AND REVISE EACH SOLUTION ===
        validated_solutions = []
        for i, solution in enumerate(solution_strategies):
            validated = await self.revise(
                instruction=f"""Critique and revise this solution. Check for:
                (a) Arithmetic errors - verify each calculation
                (b) Unit mismatches - ensure conversions are applied correctly
                (c) Logical sequence - steps must follow problem chronology
                (d) Constraint violations - no negative/invalid values
                If errors found: CORRECT them and explain fix in [REVISION NOTE].
                If no errors: CONFIRM each step with [VERIFIED].
                Preserve original structure but enhance rigor.
                Final answer must remain boxed at end.""",
                context=solution
            )
            validated_solutions.append(validated)

        # === PHASE 5: ENSEMBLE FINAL ANSWER WITH RIGOROUS SELECTION ===
        final_answer = await self.ensemble(
            instruction="""Select the best final answer from these validated solutions. Criteria:
            1. Prefer solutions with explicit revision notes confirming fixes
            2. Then prefer solutions with clearest unit handling
            3. Then prefer solutions matching narrative chronology
            If all solutions have errors, synthesize new answer by combining correct parts.
            OUTPUT ONLY THE NUMERICAL ANSWER (integer or decimal) - NO TEXT, NO UNITS.
            Example: 70""",
            contexts_list=validated_solutions
        )

        # === PHASE 6: EXTRACTION AND SANITIZATION ===
        # Extract just the number from the final answer (defensive parsing)
        match = re.search(r'[\d\.]+', final_answer.strip())
        if match:
            return match.group(0)
        else:
            # Fallback: return raw if no number found (shouldn't happen with good ensemble)
            return final_answer.strip()