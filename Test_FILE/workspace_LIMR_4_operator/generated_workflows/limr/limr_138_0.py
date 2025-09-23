# Workflow ID: limr_138_0
# Benchmark: limr
# Data Indices: [105, 193]

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

        # Step 1: Initial Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it into one of the following categories:
            - Geometry (coordinate, vector, synthetic)
            - Number Theory (modular arithmetic, divisibility, primes)
            - Algebra (polynomials, equations, inequalities)
            - Combinatorics (counting, probability, permutations)
            - Optimization (maxima/minima, inequalities)
            - Sequence and Series (recursive, summations)
            
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Using coordinate geometry, solve the problem: {analysis}",
                context=""
            ),
            self.generate(
                instruction=f"Using vector analysis, solve the problem: {analysis}",
                context=""
            ),
            self.generate(
                instruction=f"Using algebraic manipulation, solve the problem: {analysis}",
                context=""
            )
        )

        # Step 3: Iterative Refinement with Feedback
        refined_solutions = []
        for path in solution_paths:
            refined = await self.revise(
                instruction="Refine the solution by verifying calculations, addressing gaps, and improving clarity.",
                context=path
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Synthesis
        synthesis = await self.ensemble(
            instruction="Synthesize the best insights from all solution paths into a unified solution.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification and Output
        final_verification = await self.revise(
            instruction="Verify the solution for consistency, logical coherence, and adherence to constraints. Ensure the final answer is an integer between 000 and 999.",
            context=synthesis
        )

        return final_verification