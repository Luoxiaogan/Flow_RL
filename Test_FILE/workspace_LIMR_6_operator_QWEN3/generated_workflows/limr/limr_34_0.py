# Workflow ID: limr_34_0
# Benchmark: limr
# Data Indices: [198, 77]

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

        # PHASE 1: Problem Decomposition & Classification
        decomposition_plan = await self.decompose(
            instruction="""Systematically break down this mathematical problem into atomic subproblems. For each subproblem:
            - Identify the mathematical domain (algebra, number theory, combinatorics, etc.)
            - Specify required techniques (modular arithmetic, polynomial solving, counting principles, etc.)
            - List variables and constraints (e.g., digit ranges, domain restrictions)
            - Note dependencies on other subproblems
            - Flag any potential ambiguities or edge cases
            Output a structured list with clear IDs and dependency chains.""",
            context=""
        )

        # PHASE 2: Parallel Solution Exploration
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction="""Solve the problem using ALGEBRAIC methods:
                - Translate word problems into equations
                - Apply substitutions, factorizations, or transformations
                - Maintain symbolic precision
                - Show all steps leading to final answer""",
                context=""
            ),
            self.generate(
                instruction="""Solve the problem using NUMBER THEORY methods:
                - Consider modular arithmetic, divisibility, prime factors
                - Check digit constraints in different bases if applicable
                - Use Diophantine equation techniques
                - Validate solutions against domain constraints""",
                context=""
            ),
            self.generate(
                instruction="""Solve the problem using COMBINATORIAL/LOGICAL methods:
                - Enumerate cases if feasible
                - Apply counting principles or probability rules
                - Look for symmetries or invariants
                - Use proof by contradiction or exhaustion if appropriate""",
                context=""
            )
        )

        # PHASE 3: Synthesis & Conflict Resolution
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the following solution attempts into a single coherent answer:
            - Compare methodologies and identify correct partial results
            - Resolve contradictions by cross-verifying with problem constraints
            - Preserve the most rigorous derivation steps
            - If multiple valid answers exist, combine them as specified (sum, product, etc.)
            - Format final answer as an integer between 000-999 unless otherwise specified
            - Flag any remaining uncertainties for revision""",
            contexts_list=solution_attempts
        )

        # PHASE 4: Rigorous Verification & Revision
        verified_solution = await self.revise(
            instruction="""Act as a skeptical peer reviewer:
            - Check every algebraic manipulation for errors
            - Verify all constraints are satisfied (e.g., digit validity in base systems)
            - Ensure no division by zero or invalid operations
            - Confirm final answer format matches problem requirements
            - If any flaw is found, correct it with detailed justification
            - If confident, output 'VERIFIED:' followed by the final answer""",
            context=synthesized_solution
        )

        # PHASE 5: Computational Validation (if applicable)
        # Extract computational kernel if present
        computational_kernel = await self.generate(
            instruction="""Extract any precise mathematical expression, algorithm, or calculation that requires exact computation:
            - Isolate equations, summations, or functions needing evaluation
            - Specify variable domains and constraints
            - Format as Python-ready expression if possible
            - If no computation needed, return 'NONE'""",
            context=verified_solution
        )

        final_answer = verified_solution
        if "NONE" not in computational_kernel.upper():
            try:
                computed_result = await self.programmer(
                    instruction="""Implement and execute the following mathematical computation:
                    - Use exact arithmetic (no floating-point approximations)
                    - Validate input constraints before computation
                    - Return only the final integer result
                    - Handle edge cases explicitly""",
                    context=computational_kernel,
                    max_retries=2
                )
                # Merge computation with verified solution
                final_answer = await self.ensemble(
                    instruction="""Integrate the computed result with the verified solution:
                    - Replace any placeholder values with computed result
                    - Ensure consistency with derivation steps
                    - Output final answer as integer between 000-999""",
                    contexts_list=[verified_solution, computed_result]
                )
            except Exception:
                # Fallback: use verified solution as is
                pass

        # PHASE 6: Final Sanitization & Formatting
        sanitized_answer = await self.revise(
            instruction="""Final formatting pass:
            - Extract only the numerical answer (integer between 000-999)
            - Remove all explanatory text, units, or qualifications
            - If answer is a fraction or expression, evaluate to integer as required
            - If multiple answers, sum them as specified
            - Output ONLY the three-digit integer (e.g., '123', '042', '999')""",
            context=final_answer
        )

        # Extract integer using regex as final safeguard
        match = re.search(r'\b(0\d{2}|[1-9]\d{0,2})\b', sanitized_answer)
        if match:
            return match.group(1).zfill(3)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d{1,3}', sanitized_answer)
            if numbers:
                return numbers[0].zfill(3)
            else:
                return "000"  # Ultimate fallback