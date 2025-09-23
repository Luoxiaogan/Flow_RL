# Workflow ID: mgsmbn_12_0
# Benchmark: mgsmbn
# Data Indices: [18, 73]

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

        # Step 1: Cognitive Triage - Classify problem type and extract key elements
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify primary type: sequential, rate, proportional, distribution, comparison, or other.
            2. Extract all numerical values, their units (টাকা, ঘণ্টা, জিনিস, etc.), and what they represent.
            3. Identify relationships: ratios, percentages, before/after states, constraints.
            4. Flag hidden assumptions: non-negative counts, integer requirements, real-world plausibility.
            5. Assess complexity: single-step (trivial) or multi-step (complex).
            6. Suggest 2-3 distinct solution strategies (algebraic, unitary, percentage-based, etc.).
            Format output as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategy_instructions = [
            """Solve using ALGEBRAIC approach:
            - Define variables for unknowns
            - Set up equations based on relationships
            - Solve step-by-step with full working
            - Verify solution satisfies all constraints""",
            
            """Solve using UNITARY/PROPORTIONAL approach:
            - Find value per unit or base quantity
            - Scale up/down based on given ratios
            - Handle percentages as fractions of 100
            - Show intermediate proportional steps""",
            
            """Solve using SEQUENTIAL/STEP-BY-STEP approach:
            - Process events in chronological order
            - Track state changes (deposits, withdrawals, distributions)
            - Maintain running totals with units
            - Validate at each step"""
        ]

        # Generate parallel solutions
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # Step 3: Adversarial Validation - Critique each solution
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Adversarial critique of this solution:
                - Assume this solution is WRONG. Find the most likely error: arithmetic, unit mismatch, logical flaw, or misapplied formula.
                - Check unit consistency throughout (e.g., টাকা not mixed with ঘণ্টা).
                - Verify real-world constraints (no negative pets, fractional people).
                - If no error found, strengthen justification with additional verification steps.
                - End with confidence assessment (high/medium/low).""",
                context=sol
            ) for sol in solution_attempts]
        )

        # Step 4: Meta-Cognitive Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize solutions and critiques:
            1. Compare all three solutions and their critiques.
            2. Identify consensus: do 2+ solutions agree? If so, is the outlier explainable?
            3. Cross-examine steps: trace calculations for consistency.
            4. Resolve discrepancies: which solution best handles units and constraints?
            5. If ambiguity remains, propose a hybrid approach or flag as uncertain.
            6. Output ONLY the final numerical answer in this format: "FINAL_ANSWER: <number>"
            Be ruthless: prefer correctness over agreement.""",
            contexts_list=[f"Solution {i+1}:\n{sol}\n\nCritique {i+1}:\n{crit}" 
                          for i, (sol, crit) in enumerate(zip(solution_attempts, critiques))]
        )

        # Step 5: Answer Extraction and Sanitization
        sanitized = await self.summarize(
            instruction="""Extract and format final answer:
            - Find the number following "FINAL_ANSWER:" or equivalent.
            - If multiple numbers, select the one most consistent with problem constraints.
            - Round currency to 2 decimals, counts to integers unless fractional explicitly allowed.
            - Output ONLY the number, nothing else.""",
            context=final_answer
        )

        # Fallback: If extraction fails, return raw ensemble output
        try:
            # Extract number from text
            match = re.search(r'[-+]?\d*\.\d+|\d+', sanitized.strip())
            if match:
                answer = match.group(0)
                # Convert to int if whole number
                if '.' in answer and float(answer).is_integer():
                    return str(int(float(answer)))
                return answer
            else:
                # Fallback to ensemble output
                match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
                if match:
                    answer = match.group(0)
                    if '.' in answer and float(answer).is_integer():
                        return str(int(float(answer)))
                    return answer
                return "0"  # Ultimate fallback
        except:
            return "0"