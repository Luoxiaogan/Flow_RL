# Workflow ID: limr_119_0
# Benchmark: limr
# Data Indices: [54, 145]

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

        # STEP 1: CLASSIFY PROBLEM & IDENTIFY STRATEGIES
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain: Algebra, Geometry, Number Theory, Combinatorics, or Optimization.
            2. List required mathematical techniques (e.g., calculus, modular arithmetic, combinatorial identities).
            3. Flag potential pitfalls or non-obvious insights needed.
            4. Suggest 2-3 distinct solution approaches with brief rationale.
            5. Estimate complexity (low/medium/high) and number of steps required.
            Format output as structured sections with clear headings.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION
        strategy_instructions = [
            """Develop a symbolic/algebraic solution approach:
            - Use formal mathematical notation
            - Show all derivation steps
            - Justify each transformation
            - Identify critical points or constraints""",
            
            """Develop a geometric/visual solution approach:
            - Describe spatial relationships
            - Use coordinate systems if applicable
            - Leverage symmetry or invariants
            - Include diagram descriptions if helpful""",
            
            """Develop a computational/algorithmic approach:
            - Outline step-by-step procedure
            - Identify key variables and loops
            - Consider edge cases and boundary conditions
            - Prepare for potential code implementation"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: SYNTHESIZE BEST APPROACH
        synthesized_approach = await self.ensemble(
            instruction="""Select and synthesize the most promising solution approach:
            - Choose the approach with clearest path to exact integer answer
            - Merge complementary insights from other approaches if beneficial
            - Ensure all constraints and edge cases are addressed
            - Output should be a complete, step-by-step solution plan""",
            contexts_list=strategy_attempts
        )

        # STEP 4: ITERATIVE REFINEMENT (max 2 iterations)
        current_solution = synthesized_approach
        for iteration in range(2):
            critique = await self.generate(
                instruction=f"""Critically review this solution:
                - Check for algebraic errors or logical gaps
                - Verify all constraints are satisfied
                - Identify any missing edge cases
                - Assess computational feasibility
                - Suggest specific improvements
                Current iteration: {iteration + 1}""",
                context=current_solution
            )
            
            if "no errors found" in critique.lower() or "correct" in critique.lower():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise solution based on critique:
                - Fix all identified errors
                - Strengthen weak arguments
                - Add missing steps or justifications
                - Maintain mathematical rigor
                Critique: {critique}""",
                context=current_solution
            )

        # STEP 5: COMPUTATIONAL VERIFICATION
        verification_code = await self.programmer(
            instruction=f"""Generate Python code to verify key result:
            - Implement core calculation from solution
            - Include input validation and edge cases
            - Output should be the final integer answer (000-999)
            - Add comments explaining each step
            Base solution: {current_solution}""",
            context=current_solution,
            max_retries=2
        )

        # STEP 6: FINAL ANSWER EXTRACTION & FORMATTING
        final_answer = await self.revise(
            instruction="""Extract final answer as integer 000-999:
            - If answer is a pair/tuple, sum components or use primary value
            - If fractional, multiply by 100 and round to nearest integer
            - If multiple values, sum them
            - Output ONLY the 3-digit integer with leading zeros if needed
            - Justify extraction method based on problem requirements""",
            context=f"Solution: {current_solution}\n\nVerification: {verification_code}"
        )

        # Clean output to ensure 3-digit format
        digits = re.sub(r'\D', '', final_answer)
        if len(digits) > 3:
            digits = digits[-3:]
        elif len(digits) < 3:
            digits = digits.zfill(3)
            
        return digits