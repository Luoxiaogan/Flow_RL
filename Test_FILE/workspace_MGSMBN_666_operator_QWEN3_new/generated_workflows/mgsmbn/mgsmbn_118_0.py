# Workflow ID: mgsmbn_118_0
# Benchmark: mgsmbn
# Data Indices: [89]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Break problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Systematically decompose this Bengali math word problem into atomic subproblems. For each subproblem:
            - Identify the core question or calculation needed
            - Extract all relevant quantities, units, and entities (teachers, items, time periods, etc.)
            - Specify dependencies: which subproblems must be solved first?
            - Note any constraints or conditions (e.g., "per day", "each person", "if...then")
            - Flag any ambiguous phrases that need clarification
            Output as a dependency-ordered list of subproblems.""",
            context=""
        )

        # STEP 2: PARALLEL INTERPRETATION - Generate 3 independent readings of key values/relationships
        interpretation_tasks = [
            self.generate(
                instruction="""Extract all numerical values and their semantic relationships from the problem. Focus on:
                - Verbs and actions: what is being done? (e.g., "মোছা হয়" = erased)
                - Quantifiers: "প্রতি" (per), "প্রত্যেক" (each), "মোট" (total)
                - Temporal markers: "প্রতিদিন" (daily), "প্রতি ঘণ্টা" (hourly)
                - Entity-quantity mappings: who/what has how many of what?
                Format as: [Entity] → [Quantity] [Unit] [Relationship]""",
                context=""
            ),
            self.generate(
                instruction="""Extract all numerical values by focusing on modifying phrases and prepositions:
                - Look for "X এর জন্য Y" (for X, Y times)
                - Identify rate structures: "প্রতি A তে B" (B per A)
                - Capture nested quantities: "each of X does Y, and each Y requires Z"
                - Map hierarchical relationships: teachers → chapters → erasures
                Format as a nested bullet list showing dependency chains.""",
                context=""
            ),
            self.generate(
                instruction="""Extract quantities by simulating the scenario chronologically:
                - What happens first? Who acts first?
                - What changes with each action? (e.g., erasures accumulate)
                - Track state changes: after Teacher 1's first chapter, erasures = 3
                - Identify termination condition: when does the process end? (e.g., after all teachers)
                Format as a step-by-step state log with cumulative totals.""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)

        # STEP 3: CONSENSUS ENSEMBLE - Reconcile interpretations into unified problem model
        unified_model = await self.ensemble(
            instruction="""Synthesize these three interpretations into a single, validated problem model. Your goals:
            1. Resolve discrepancies: if interpretations disagree on a quantity, determine the correct reading from context.
            2. Fill gaps: if any interpretation misses a key relationship, add it from others.
            3. Structure output as:
               - Entities: [list with quantities]
               - Relationships: [list with formulas, e.g., "total erasures = teachers × chapters_per_teacher × erasures_per_chapter"]
               - Constraints: [list, e.g., "all teachers participate", "no fractional erasures"]
               - Goal: [explicitly state what to solve for]
            4. Flag any remaining ambiguities that need assumption.""",
            contexts_list=interpretations
        )

        # STEP 4: DUAL SOLUTION STRATEGY GENERATION - Algebraic and procedural approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate an ALGEBRAIC solution strategy based on this model:
                {unified_model}
                
                Steps:
                1. Define variables for unknowns (if any) and knowns.
                2. Write equation(s) relating quantities.
                3. Show substitution steps.
                4. Specify final computation.
                5. Include unit tracking: ensure dimensions match (e.g., erasures/day).
                Output as a step-by-step symbolic derivation.""",
                context=unified_model
            ),
            self.generate(
                instruction=f"""Generate a PROCEDURAL simulation strategy based on this model:
                {unified_model}
                
                Steps:
                1. Initialize state (e.g., total_erasures = 0).
                2. Loop through entities chronologically (e.g., for each teacher...).
                3. Within each entity, loop through actions (e.g., for each chapter...).
                4. Accumulate results (e.g., add erasures per action).
                5. Return final state.
                Output as pseudocode with clear loops and accumulators.""",
                context=unified_model
            )
        ]
        
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # STEP 5: STRATEGY REFINEMENT - Add rigor, units, edge cases
        refined_strategies = []
        for i, strategy in enumerate(raw_strategies):
            refined = await self.revise(
                instruction=f"""Improve this solution strategy:
                - Add explicit unit tracking at every step (e.g., "3 erasures/chapter × 2 chapters/teacher = 6 erasures/teacher")
                - Handle edge cases: what if quantities were zero? What if relationships changed?
                - Ensure no steps are skipped — show all intermediate calculations.
                - Verify dimensional consistency: final answer must match goal's units.
                - If any assumption is made, state it explicitly.
                Original strategy type: {'Algebraic' if i == 0 else 'Procedural'}""",
                context=strategy
            )
            refined_strategies.append(refined)

        # STEP 6: DUAL CODE GENERATION - Implement both strategies
        code_tasks = [
            self.programmer(
                instruction=f"""Implement this ALGEBRAIC solution as Python code:
                {refined_strategies[0]}
                
                Requirements:
                - Use descriptive variable names (e.g., teachers_count, erasures_per_chapter).
                - Include comments explaining each step.
                - Print only the final numerical answer (no units in output).
                - Validate input assumptions (e.g., assert teachers_count > 0).
                - Handle potential float/int conversion if needed.""",
                context=refined_strategies[0]
            ),
            self.programmer(
                instruction=f"""Implement this PROCEDURAL solution as Python code:
                {refined_strategies[1]}
                
                Requirements:
                - Use loops and accumulators as described.
                - Include comments for each loop level.
                - Print only the final numerical answer.
                - Validate loop bounds (e.g., range(teachers_count)).
                - Ensure integer arithmetic where appropriate.""",
                context=refined_strategies[1]
            )
        ]
        
        code_results = await asyncio.gather(*code_tasks)

        # STEP 7: CROSS-VALIDATION ENSEMBLE - Reconcile code outputs
        validation_result = await self.ensemble(
            instruction="""Compare these two code execution results. Your task:
            1. Extract the numerical answer from each.
            2. If they match, return that number as a string.
            3. If they differ:
               - Analyze which code likely has the error (check logic, loops, arithmetic).
               - Revise the erroneous code conceptually.
               - Recompute manually using corrected logic.
               - Return the corrected answer.
            4. If both are wrong, use the unified_model to derive correct answer manually.
            Output ONLY the final numerical answer as a string (e.g., "24").""",
            contexts_list=code_results
        )

        # STEP 8: SANITY CHECK - Validate answer against real-world constraints
        final_answer = await self.generate(
            instruction=f"""Perform a final sanity check on this answer: {validation_result}
            Consider:
            - Is the answer an integer? (Erasures can't be fractional — round if needed)
            - Is the magnitude reasonable? (e.g., 24 erasures/day for 4 teachers is plausible)
            - Does it match the problem's goal? (Total daily erasures)
            - Are units consistent? (Answer should be a pure number — no 'times' or 'erasures')
            If any issue, correct it. Otherwise, return the answer unchanged.
            Output ONLY the final numerical answer as a string.""",
            context=validation_result
        )

        # Extract numerical answer (robustly handle any residual text)
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return raw validation result if parsing fails
            return validation_result.strip()