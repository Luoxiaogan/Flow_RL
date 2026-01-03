# Workflow ID: mgsmbn_87_0
# Benchmark: mgsmbn
# Data Indices: [182, 42]

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

        # === PHASE 1: SEMANTIC DECOMPOSITION ===
        decomposition = await self.generate(
            instruction="""
            Perform deep semantic decomposition of this Bengali math word problem.
            Identify and structure the following components:
            - ENTITIES: All people, objects, or groups mentioned (e.g., Andrew, cats, bus, car)
            - QUANTITIES: All numerical values with their descriptions (e.g., "6 days", "7 kittens")
            - RELATIONSHIPS: Mathematical or logical connections (e.g., "half the time", "three times as many")
            - CONSTRAINTS: Real-world or contextual limits (e.g., "must be whole number", "round trip")
            - UNKNOWN: What is being asked? Express it as a mathematical target.
            Format each section clearly with headers. Think step by step like a math teacher explaining to a student.
            """,
            context=""
        )

        # === PHASE 2: PARALLEL HYPOTHESIS GENERATION ===
        modeling_strategies = [
            """
            Strategy A: Chronological Modeling
            Reconstruct the problem as a timeline of events. Assign variables to unknowns.
            Express each step as a mathematical operation in sequence. Track units at every step.
            Example: If going takes X days and returning takes X/2, total = X + X/2.
            """,
            """
            Strategy B: Algebraic Modeling
            Define variables for unknowns. Write equations based on relationships.
            Solve symbolically first, then substitute numbers. Show all algebraic steps.
            Check for dimensional consistency (units must match on both sides of equations).
            """,
            """
            Strategy C: Unit Propagation & Proportional Reasoning
            Focus on how units transform through operations. Use proportions and scaling.
            If "A is three times B", express as A = 3B. Track what each number represents.
            Validate that final units match the question's requirement (e.g., days, cats, etc.).
            """
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(
                instruction=f"""
                Based on the problem decomposition:
                {decomposition}

                Apply the following strategy to build a complete solution:
                {strategy}

                Requirements:
                - Show every calculation step explicitly.
                - Annotate what each number represents (include units).
                - State the final answer clearly at the end.
                - If any step produces a fractional entity (e.g., 0.5 cats), flag it as invalid.
                """,
                context=decomposition
            ) for strategy in modeling_strategies]
        )

        # === PHASE 3: CRITIQUE & REFINEMENT ===
        refined_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            refined = await self.revise(
                instruction=f"""
                Critically evaluate this solution attempt (Strategy {chr(65+i)}).

                Check for:
                1. Mathematical correctness: Do operations follow from premises?
                2. Unit consistency: Are units preserved and appropriate?
                3. Real-world plausibility: Are fractional entities avoided where impossible?
                4. Completeness: Does it answer the exact question asked?
                5. Clarity: Are steps well-explained and traceable?

                If errors are found, correct them. If ambiguous, state assumptions.
                Preserve the final numerical answer format.
                """,
                context=hypothesis
            )
            refined_hypotheses.append(refined)

        # === PHASE 4: SYNTHESIS & SELECTION ===
        best_solution = await self.ensemble(
            instruction="""
            You are given multiple solution attempts for the same Bengali math problem.
            Select the BEST solution based on:
            - Mathematical soundness (correct operations, no logical leaps)
            - Unit and constraint adherence (no fractional cats, correct units)
            - Clarity and completeness (all steps shown, answer clearly stated)
            - Alignment with problem narrative (matches story context)

            If multiple are equally valid, choose the simplest or most direct.
            Output ONLY the selected solution in full — do not summarize.
            """,
            contexts_list=refined_hypotheses
        )

        # === PHASE 5: FINAL VERIFICATION & ANSWER EXTRACTION ===
        verified_answer = await self.revise(
            instruction="""
            Extract the FINAL NUMERICAL ANSWER from the solution below.
            Requirements:
            - The answer must be a single number (integer or decimal).
            - Remove all units, explanations, or text.
            - If the solution contains multiple numbers, select the one that answers the question.
            - If no clear number is found, return "ERROR".

            Example valid outputs: "9", "40.5", "12"
            """,
            context=best_solution
        )

        # Clean and return final answer
        # Strip non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', verified_answer.strip())
        if cleaned.count('.') <= 1 and cleaned.replace('.', '').isdigit():
            return cleaned
        else:
            # Fallback: return as-is if cleaning fails (let grading handle it)
            return verified_answer.strip()