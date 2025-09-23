# Workflow ID: mgsmbn_4_0
# Benchmark: mgsmbn
# Data Indices: [178, 171]

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

        # STEP 1: DECOMPOSE THE PROBLEM INTO STRUCTURED COMPONENTS
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into its core semantic and mathematical components. Extract and explicitly list:
            - All named entities (people, objects, places) and their roles
            - All numerical values with their associated units and what they represent
            - All actions or events in chronological or logical order
            - All relationships between quantities (e.g., "twice as much", "50 more than")
            - The explicit question being asked and the unknown to solve for
            - Any constraints or real-world limitations (e.g., no negative quantities, integer people)
            Format as a structured markdown list with clear section headers. Be exhaustive — missing details cause errors later.""",
            context=""
        )

        # STEP 2: CLASSIFY PROBLEM TYPE TO GUIDE SOLUTION STRATEGY
        classification = await self.generate(
            instruction=f"""Based on the decomposition below, classify this problem into one or more of these categories:
            - Sequential Operations (actions happening in steps: deposit, then withdraw)
            - Rate Problems (involving speed, unit price, work rate: per hour, per item)
            - Proportional Reasoning (ratios, percentages, fractions, scaling: twice, half, 25%)
            - Distribution (dividing, sharing, remainders: among 5 people, equally)
            - Comparison (differences, "how many more", "less than")
            - Multi-entity Tracking (multiple people/objects with different quantities)
            
            Also determine:
            - Required operations: addition, subtraction, multiplication, division, algebra?
            - Expected answer format: integer, decimal, with/without units?
            - Potential pitfalls: hidden steps, ambiguous phrasing, unit conversions?
            
            Output as a JSON-like structure with keys: "categories", "operations", "format", "pitfalls".
            Use the decomposition for context:
            {decomposition}""",
            context=decomposition
        )

        # STEP 3: GENERATE MULTIPLE SOLUTION ATTEMPTS IN PARALLEL
        # Each attempt uses a different mathematical lens based on classification
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP ARITHMETIC SIMULATION:
                - Start from initial values mentioned in the problem.
                - Apply each action/event in chronological order.
                - Show intermediate results after each operation.
                - Track units explicitly at every step.
                - Verify no step violates real-world constraints (no negative water, fractional people).
                - End with the final numerical answer.
                Base your simulation on this decomposition and classification:
                {decomposition}
                {classification}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                - Define variables for unknowns.
                - Translate relationships into equations (e.g., "twice the remaining" → 2*x).
                - Solve the system step by step, showing algebraic manipulation.
                - Substitute known values and compute final answer.
                - Validate that solution fits all constraints.
                Use this context:
                {decomposition}
                {classification}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using PROPORTIONAL/UNIT ANALYSIS:
                - Identify base quantities and scaling factors.
                - Set up ratios, fractions, or percentage relationships.
                - Cross-multiply or scale as needed.
                - Track how units transform or cancel.
                - Compute final value and verify against total constraints.
                Context:
                {decomposition}
                {classification}""",
                context=decomposition
            )
        )

        # STEP 4: ENSEMBLE — COMPARE AND SYNTHESIZE BEST SOLUTION
        synthesized_solution = await self.ensemble(
            instruction="""You are given multiple solution attempts for the same Bengali math problem.
            Your task:
            1. Compare all solutions for numerical consistency — do they arrive at the same final value?
            2. Evaluate each for logical flow: are steps justified? Are units preserved?
            3. Check for constraint violations: negative quantities? Fractional people? Illogical intermediates?
            4. If all agree and are valid, output any one.
            5. If they disagree, select the solution that:
               - Matches the problem's chronological/logical structure
               - Preserves units correctly
               - Has no constraint violations
               - Shows clearest intermediate reasoning
            6. If no solution is fully valid, synthesize a corrected version by combining valid parts.
            Output the chosen or synthesized solution in full, with all steps and final answer.""",
            contexts_list=solution_attempts
        )

        # STEP 5: REVISE & VALIDATE — UP TO 2 ITERATIONS
        current_solution = synthesized_solution
        for iteration in range(2):
            validation = await self.revise(
                instruction=f"""CRITICALLY VALIDATE THIS SOLUTION:
                - Re-calculate every arithmetic step. Flag any miscalculation.
                - Verify unit consistency: do liters stay liters? Do counts stay integers?
                - Check against real-world constraints: no negative water, no 0.5 people.
                - Ensure chronological/logical order matches problem narrative.
                - If any error found, correct it explicitly and recompute affected steps.
                - If no errors, output "VALID" followed by the solution.
                Current solution:
                {current_solution}""",
                context=current_solution
            )
            
            if "VALID" in validation:
                current_solution = validation.replace("VALID", "").strip()
                break
            else:
                current_solution = validation  # Use corrected version for next iteration

        # STEP 6: EXTRACT FINAL NUMERICAL ANSWER
        final_answer = await self.summarize(
            instruction="""From the validated solution below, extract ONLY the final numerical answer.
            - If decimal, preserve necessary precision (e.g., 25.5 not 25.5000)
            - If integer, output as integer (e.g., 90 not 90.0)
            - NO units, NO explanations, NO text — just the number.
            - If multiple numbers appear, select the one that answers the original question.
            Solution:
            """ + current_solution,
            context=current_solution
        )

        return final_answer.strip()