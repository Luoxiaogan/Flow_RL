# Workflow ID: mgsmbn_46_0
# Benchmark: mgsmbn
# Data Indices: [59, 50]

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

        # STEP 1: CLASSIFY & EXTRACT — Understand the problem's structure
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem. Your task is to:

1. Classify the problem type: Is it about rates, comparisons, distributions, sequential operations, or multi-entity relationships?
2. Extract all numerical values and what they represent (e.g., "175 diamonds", "$2.50 per package").
3. Identify all entities (people, objects, groups) and their associated quantities or roles.
4. Infer relationships between quantities (e.g., "35 less than", "twice as many").
5. Determine the unknown being asked for and its expected unit/format.
6. Note any constraints (e.g., must be integer, non-negative, exact value).

Present your analysis in a structured, bullet-point format. Be exhaustive — do not skip implicit relationships.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis:
{problem_analysis}

Develop a detailed, step-by-step solution strategy using ALGEBRAIC MODELING. Define variables, write equations, and solve symbolically. Show how to isolate the unknown. Justify each step with reference to the problem text.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
{problem_analysis}

Develop a detailed, step-by-step solution strategy using ARITHMETIC SEQUENCING. Break the problem into discrete calculation steps in chronological or logical order. Specify exactly what to calculate at each step and why. Track units throughout.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
{problem_analysis}

Develop a detailed, step-by-step solution strategy using UNIT/PROPORTIONAL REASONING. Focus on ratios, unit prices, scaling, or rate conversions. Show how to normalize quantities for comparison or aggregation. Emphasize dimensional consistency.""",
                context=problem_analysis
            )
        ]

        solution_strategies = await asyncio.gather(*strategy_tasks)

        # STEP 3: ENSEMBLE — SELECT OR SYNTHESIZE THE BEST STRATEGY
        best_strategy = await self.ensemble(
            instruction="""You are given multiple solution strategies for the same Bengali math word problem. Your task:

1. Compare them for completeness, logical flow, and alignment with the problem's constraints.
2. Check for missing steps, unit mismatches, or arithmetic oversights.
3. Prefer strategies that explicitly handle edge cases (e.g., remainders, fractional results when integers are expected).
4. If one strategy is clearly superior, select it. If multiple are strong, synthesize a hybrid that combines their best elements.
5. Output a single, refined, step-by-step solution plan with numbered steps.

CRITICAL: The final plan must be executable — each step must specify a concrete calculation or logical operation.""",
            contexts_list=solution_strategies
        )

        # STEP 4: EXECUTE & REVISE EACH STEP ITERATIVELY
        steps = best_strategy.strip().split('\n')
        cleaned_steps = [s for s in steps if re.match(r'^\d+[\.\)]', s.strip())]  # Extract numbered steps
        verified_steps = []

        for i, step in enumerate(cleaned_steps):
            # Generate the calculation for this step
            calculation = await self.generate(
                instruction=f"""Execute ONLY this step from the solution plan:
"{step}"

Perform the exact calculation or logical operation required. Show your work. Include units if applicable. Output ONLY the result and a brief justification — no extra text.""",
                context=best_strategy
            )

            # Revise/verify the calculation
            verified = await self.revise(
                instruction=f"""Critically verify this calculation:
"{calculation}"

Check for:
- Arithmetic accuracy
- Unit consistency with previous steps and problem context
- Logical alignment with the step's intent
- Plausibility (e.g., no negative counts, fractional people)

If correct, return it unchanged. If flawed, correct it and explain the fix. Output ONLY the final verified result.""",
                context=calculation
            )
            verified_steps.append(verified)

        # STEP 5: SYNTHESIZE FINAL ANSWER
        final_answer_draft = await self.generate(
            instruction=f"""Based on these verified step results:
{''.join([f"Step {i+1}: {v}" for i, v in enumerate(verified_steps)])}

Synthesize the FINAL NUMERICAL ANSWER to the original problem. Extract only the number — no units, no explanation, no text. If the answer is decimal, preserve necessary precision. If integer expected, round appropriately.""",
            context="\n".join(verified_steps)
        )

        # STEP 6: SANITY CHECK & FINAL REVISION
        sanity_check = await self.generate(
            instruction=f"""SANITY CHECK: Does this answer make sense?
Answer: {final_answer_draft}

Verify:
- Is it numerically plausible given the problem's scale?
- Does it match expected format (integer/decimal)?
- Does it satisfy all constraints from the original analysis?
- Is it positive/non-negative where required?

If it fails ANY check, revise it. Otherwise, return it unchanged. OUTPUT ONLY THE FINAL NUMBER.""",
            context=final_answer_draft
        )

        # Extract clean numerical answer
        match = re.search(r'[-+]?\d*\.\d+|\d+', sanity_check.replace(',', ''))
        if match:
            final_answer = match.group(0)
            # Convert to int if it's a whole number
            if '.' in final_answer and float(final_answer).is_integer():
                final_answer = str(int(float(final_answer)))
        else:
            final_answer = "0"  # Fallback

        return final_answer