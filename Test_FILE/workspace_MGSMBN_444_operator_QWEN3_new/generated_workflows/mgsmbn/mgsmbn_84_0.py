# Workflow ID: mgsmbn_84_0
# Benchmark: mgsmbn
# Data Indices: [57, 166]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Extract structured problem schema
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify:

1. ENTITIES: All objects, people, or concepts involved (e.g., dog, cakes, days, bags).
2. PHASES/CONDITIONS: Temporal or logical segments (e.g., "first 180 days", "after that", "Monday/Tuesday/Wednesday").
3. QUANTITIES & UNITS: All numerical values with their associated units (e.g., "1 cup/day", "110 cups/bag").
4. RELATIONSHIPS: Mathematical dependencies (e.g., "three times Tuesday's amount", "for the rest of its life").
5. TARGET: What is being asked for? (e.g., "number of bags", "total cakes").

Format your output STRICTLY as:
ENTITIES: [comma-separated list]
PHASES: [numbered list with descriptions]
QUANTITIES: [labeled values with units]
RELATIONSHIPS: [mathematical expressions or descriptions]
TARGET: [exact question being asked]

Be exhaustive. Do not solve—only structure.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION GENERATION - Three distinct approaches
        solution_tasks = [
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
Given decomposition: {decomposition}

1. Define variables for unknowns.
2. Write equations for each phase/relationship.
3. Solve step-by-step with substitutions.
4. Show all intermediate calculations.
5. Box final answer.

Focus on mathematical rigor. Track units throughout.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using ITERATIVE/STEP-BY-STEP NARRATIVE:
Given decomposition: {decomposition}

1. Walk through the problem chronologically or logically.
2. At each step, state: "At this stage, we have..."
3. Calculate cumulative totals incrementally.
4. Explicitly handle phase transitions (e.g., "After day 180...").
5. Box final answer.

Focus on clarity and real-world plausibility.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using UNIT ANALYSIS & PROPORTIONAL REASONING:
Given decomposition: {decomposition}

1. Identify base units (cups, days, bags, etc.).
2. Set up conversion chains (e.g., cups → bags).
3. Use ratios/proportions for multiplicative relationships.
4. Apply dimensional analysis to verify steps.
5. Box final answer.

Focus on unit consistency and scaling logic.""",
                context=decomposition
            )
        ]
        
        # Run solutions in parallel
        algebraic_sol, iterative_sol, unit_sol = await asyncio.gather(*solution_tasks)

        # STEP 3: ENSEMBLE SYNTHESIS - Cross-validate and merge
        final_solution = await self.ensemble(
            instruction="""You are an expert math validator. You have three solution attempts for the same Bengali word problem:

1. ALGEBRAIC APPROACH: [provided]
2. ITERATIVE NARRATIVE: [provided]  
3. UNIT ANALYSIS: [provided]

Your task:
- Compare numerical answers. Do they agree?
- If they disagree, identify which solution correctly handles all phases, units, and constraints from the decomposition.
- Check for: correct phase boundaries, unit conversions, multiplicative relationships, and real-world plausibility (e.g., no fractional bags if context implies whole units).
- Synthesize the most rigorous, complete solution. Preserve step-by-step reasoning.
- If all solutions have flaws, create a corrected version by combining their strengths.

Output ONLY the final, validated solution with clear steps and boxed answer.""",
            contexts_list=[algebraic_sol, iterative_sol, unit_sol]
        )

        # STEP 4: VALIDATION & REVISION LOOP (max 2 iterations)
        for attempt in range(2):
            validation = await self.generate(
                instruction=f"""SANITY CHECKER: Validate this solution against the original problem and decomposition.

Decomposition: {decomposition}
Solution: {final_solution}

Checklist:
1. Does the answer match the TARGET from decomposition?
2. Are all PHASES/CONDITIONS accounted for? (e.g., first 180 days vs. after)
3. Are UNITS consistent and correctly converted? (e.g., cups → bags)
4. Are QUANTITIES non-negative and plausible? (e.g., no 0.3 dogs)
5. Are RELATIONSHIPS correctly applied? (e.g., "three times" = ×3)

If any issue is found, describe it SPECIFICALLY. If perfect, say "VALID".

Output format:
STATUS: [VALID or INVALID]
ISSUES: [bullet list of specific errors, if any]""",
                context=final_solution
            )

            if "STATUS: VALID" in validation:
                break
            else:
                # Revise using validation feedback
                final_solution = await self.revise(
                    instruction=f"""REVISE based on validation feedback:

Validation Report: {validation}

Original Decomposition: {decomposition}

Instructions:
1. Address EVERY issue listed in ISSUES.
2. Preserve correct parts of the solution.
3. Re-calculate only affected steps.
4. Maintain clear step-by-step reasoning.
5. Box the corrected final answer.

Do NOT change correct calculations. Focus only on fixing identified flaws.""",
                    context=final_solution
                )
        else:
            # If loop exhausted, use best available
            pass

        # STEP 5: ANSWER EXTRACTION - Isolate numerical answer
        answer = await self.generate(
            instruction="""Extract ONLY the numerical answer from this solution. Rules:

- If integer (e.g., 5), output "5"
- If decimal (e.g., 5.5), output "5.5"
- NO units, NO text, NO explanation
- If multiple numbers, choose the FINAL answer
- Round only if explicitly required by problem

Example: If solution ends with "∴ Total bags = 5", output "5"

Output ONLY the number as a string.""",
            context=final_solution
        )

        # Clean answer (remove any accidental text)
        answer = re.sub(r'[^\d\.]', '', answer.strip())
        
        return answer