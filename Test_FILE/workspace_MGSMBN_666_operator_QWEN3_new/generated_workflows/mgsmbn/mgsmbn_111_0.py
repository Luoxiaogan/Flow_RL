# Workflow ID: mgsmbn_111_0
# Benchmark: mgsmbn
# Data Indices: [10]

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
        import json

        # STEP 1: Decompose the problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Break down the Bengali word problem into atomic, solvable subproblems. 
            For each subproblem:
            - Identify the quantity or relationship being asked or given
            - Specify dependencies (which other subproblems must be solved first)
            - Note units, constraints, and implicit assumptions
            - Flag any ambiguous phrasing that requires interpretation
            Output as a list of dictionaries with 'id', 'description', and 'dependencies' keys.""",
            context=""
        )

        # STEP 2: Generate three parallel solution strategies
        strategy_instructions = [
            """Develop an ALGEBRAIC solution strategy:
            - Represent unknowns as variables
            - Formulate equations based on relationships in the problem
            - Solve symbolically step by step
            - Substitute known values only at the end
            - Show all equation transformations
            - Validate that final answer matches problem constraints""",
            
            """Develop an ARITHMETIC solution strategy:
            - Use only direct numerical operations (no variables)
            - Compute step-by-step in chronological or logical order
            - At each step, state what you're calculating and why
            - Track units explicitly (টাকা, জন, শতাংশ, etc.)
            - Round only at final step if required
            - Verify intermediate values make real-world sense""",
            
            """Develop a PROPORTIONAL/RELATIONAL solution strategy:
            - Focus on ratios, percentages, fractions, or scaling
            - Express relationships as proportions (A:B = C:D)
            - Use cross-multiplication or unitary method where applicable
            - Highlight how parts relate to wholes
            - Check that proportional splits sum correctly (e.g., percentages to 100%)
            - Handle 'remaining' or 'rest' as derived quantities"""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=json.dumps(decomposition, ensure_ascii=False)) 
              for instr in strategy_instructions]
        )

        # STEP 3: Critique and refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically review this solution strategy:
                - Check for mathematical consistency and correct order of operations
                - Verify unit tracking and conversions
                - Ensure no unsupported assumptions (e.g., fractional people)
                - Flag any step that contradicts problem constraints
                - Suggest improvements for clarity and rigor
                - If strategy is fundamentally flawed, explain why""",
                context=strat
            ) for strat in strategies]
        )

        # STEP 4: Convert refined strategies to executable code
        code_solutions = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Generate Python code that implements this solution strategy exactly.
                Requirements:
                - Use only basic arithmetic operations and math library
                - Include assertions to validate intermediate values (e.g., non-negative, percentage <= 100)
                - Handle units symbolically (no unit conversion unless explicitly required)
                - Return ONLY the final numerical answer as a float or int
                - Add comments mapping each code block to strategy steps
                - If strategy is invalid, raise ValueError with explanation""",
                context=refined_strat,
                max_retries=3
            ) for refined_strat in refined_strategies]
        )

        # STEP 5: Ensemble - Synthesize and select best answer
        final_answer = await self.ensemble(
            instruction="""Compare the three numerical outputs:
            - If all three agree, return that value
            - If two agree, return the majority value
            - If all differ, select the answer from the most mathematically rigorous and traceable solution
            - Validate that the chosen answer satisfies all problem constraints (e.g., non-negative, within percentage bounds)
            - Return ONLY the final numerical value as a string (e.g., "60", "15.5")""",
            contexts_list=code_solutions
        )

        # STEP 6: Meta-validation (optional refinement loop)
        # If ensemble result seems inconsistent, trigger refinement
        validation = await self.generate(
            instruction=f"""Validate the final answer: {final_answer}
            - Does it satisfy all constraints from the original problem?
            - Is it consistent with the decomposed subproblems?
            - Are units and scale appropriate (e.g., not 150% for a percentage problem)?
            - If any red flags, suggest a corrected approach.
            Return 'VALID' if acceptable, or 'INVALID: [reason]' if not.""",
            context=f"Decomposition: {json.dumps(decomposition)}\nFinal Answer: {final_answer}"
        )

        if "INVALID" in validation:
            # Re-run with stricter constraints on the most promising strategy
            fallback_strategy = await self.revise(
                instruction=f"""Re-solve using the most reliable strategy, with strict constraints:
                - All outputs must be integers unless problem explicitly allows decimals
                - Percentages must sum to exactly 100% if covering all cases
                - No negative quantities
                - Re-check unit consistency
                Original validation issue: {validation}""",
                context=refined_strategies[0]  # Arbitrarily pick first as baseline
            )
            
            fallback_code = await self.programmer(
                instruction="""Generate Python code with strict validation:
                - Assert all intermediate values meet real-world constraints
                - Round to integer if required
                - Return only final numerical answer""",
                context=fallback_strategy,
                max_retries=3
            )
            
            final_answer = fallback_code  # Programmer returns execution result including answer

        # Extract just the numerical value from final output
        # (Programmer/Ensemble should return clean number, but sanitize just in case)
        import re
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (let grading handle it)
            return final_answer.strip()