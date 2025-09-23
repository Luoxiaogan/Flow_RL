# Workflow ID: mgsmbn_104_0
# Benchmark: mgsmbn
# Data Indices: [138, 155]

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

        # === PHASE 1: SEMANTIC DECOMPOSITION & VALIDATION ===
        decomposition = await self.generate(
            instruction="""Thoroughly decompose this Bengali word problem into structured components. Output in this exact format:

            ENTITIES:
            - List all people, objects, or groups mentioned, with their roles

            QUANTITIES:
            - List all numerical values with their units and what they represent
            - Include implicit quantities (e.g., "half", "twice")

            RELATIONSHIPS:
            - Describe mathematical or logical relationships between quantities
            - Include temporal sequences, comparisons, or dependencies

            GOAL:
            - State exactly what the problem is asking for
            - Specify the expected answer format (integer, decimal, unit)

            CONSTRAINTS:
            - List real-world or mathematical constraints (e.g., "no negative items", "must be integer")

            Be exhaustive. If any component is ambiguous, note it explicitly.""",
            context=""
        )

        # Validate decomposition completeness
        validation_feedback = await self.generate(
            instruction=f"""Critically evaluate this decomposition:

            {decomposition}

            Check for:
            1. Are ALL numerical values from the problem accounted for?
            2. Are units consistent and explicitly stated?
            3. Is the goal unambiguous and mathematically well-defined?
            4. Are there any logical gaps or missing relationships?
            5. Do the constraints reflect real-world plausibility?

            If any issues are found, describe them SPECIFICALLY. If perfect, say "VALIDATED".""",
            context=decomposition
        )

        # Revise if needed
        if "VALIDATED" not in validation_feedback:
            decomposition = await self.revise(
                instruction=f"""Improve the decomposition using this feedback:

                {validation_feedback}

                Preserve the original structure but fill gaps, clarify ambiguities, and ensure mathematical completeness.
                Do not invent information — only make explicit what is implied in the problem.""",
                context=decomposition
            )

        # === PHASE 2: PARALLEL STRATEGY GENERATION ===
        strategy_instructions = [
            f"""Solve using CHRONOLOGICAL SIMULATION:
            - Model the problem as a sequence of state changes over time
            - Track quantities step-by-step as events unfold
            - Show intermediate values after each operation
            - Final answer must emerge naturally from the timeline
            - Use this decomposition as your foundation:
            {decomposition}""",
            
            f"""Solve using ALGEBRAIC ABSTRACTION:
            - Represent unknowns as variables
            - Derive equations from relationships in the decomposition
            - Solve symbolically before plugging in numbers
            - Show equation setup, simplification, and solution
            - Use this decomposition as your foundation:
            {decomposition}""",
            
            f"""Solve using UNIT PROPAGATION & DIMENSIONAL ANALYSIS:
            - Track units through every calculation
            - Convert units explicitly when needed
            - Ensure final answer has correct unit/dimension
            - Verify that operations preserve dimensional consistency
            - Use this decomposition as your foundation:
            {decomposition}"""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # === PHASE 3: ENSEMBLE SYNTHESIS WITH CONFLICT RESOLUTION ===
        synthesized_solution = await self.ensemble(
            instruction="""You are given three different solution strategies for the same problem. Your task:

            1. Compare the final numerical answers. If all agree, select the most clearly reasoned solution.
            2. If they disagree:
               - Identify WHERE and WHY the solutions diverge
               - Check which strategy best respects the problem's constraints and decomposition
               - Prefer solutions that maintain unit consistency and real-world plausibility
               - Synthesize a hybrid solution that combines the strongest elements
            3. Output ONLY the final numerical answer as a single number (integer or decimal)
               - NO explanations, NO units, NO additional text
               - If fractional, use decimal form (e.g., 3.5 not 7/2)

            Strategies to evaluate:
            """,
            contexts_list=strategies
        )

        # === PHASE 4: REALITY CHECK & FINAL VERIFICATION ===
        reality_check = await self.generate(
            instruction=f"""Verify this answer in context: {synthesized_solution}

            Generate a natural language explanation that:
            - Restates the problem in one sentence
            - Explains how the answer was derived in 2-3 steps
            - Confirms it satisfies all constraints from decomposition
            - Checks for real-world plausibility (no negative flamingos, fractional people, etc.)

            If any inconsistency is found, output "REJECT: [reason]". Otherwise, output "ACCEPT".""",
            context=decomposition
        )

        if "REJECT" in reality_check:
            # Fallback: Re-decompose with focus on conflict points
            refined_decomposition = await self.revise(
                instruction=f"""Re-analyze the problem with focus on potential misinterpretations:

                Previous decomposition had issues: {reality_check}
                Re-examine relationships and quantities, especially those involved in the conflict.
                Be extra cautious about implicit operations and unit conversions.""",
                context=decomposition
            )
            
            # Quick re-solve with algebraic approach (most robust)
            fallback_solution = await self.generate(
                instruction=f"""Solve definitively using algebraic approach:

                {refined_decomposition}

                Show all steps. Final answer must be a single number (integer or decimal).""",
                context=""
            )
            
            # Extract number from fallback solution
            match = re.search(r'[-+]?\d*\.\d+|\d+', fallback_solution)
            if match:
                synthesized_solution = match.group(0)
            else:
                # Last resort: take first strategy's answer
                match = re.search(r'[-+]?\d*\.\d+|\d+', strategies[0])
                if match:
                    synthesized_solution = match.group(0)
                else:
                    synthesized_solution = "0"  # Ultimate fallback

        return synthesized_solution