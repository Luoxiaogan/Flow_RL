# Workflow ID: limr_48_0
# Benchmark: limr
# Data Indices: [240, 275]

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

        # Initial analysis to classify the problem and identify key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify key components:
            - Problem type (geometry, number theory, algebra, combinatorics, probability)
            - Required techniques and mathematical tools
            - Constraints and conditions
            - Expected answer format (integer between 000 and 999)
            Provide a structured classification.""",
            context=""
        )

        # Branch based on problem type and required techniques
        if "geometry" in initial_analysis.lower():
            branches = await asyncio.gather(
                self.generate(
                    instruction="Solve using coordinate geometry approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using vector calculations approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using trigonometric identities approach...",
                    context=initial_analysis
                )
            )
        elif "number theory" in initial_analysis.lower():
            branches = await asyncio.gather(
                self.generate(
                    instruction="Solve using modular arithmetic approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using prime factorization approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using divisibility rules approach...",
                    context=initial_analysis
                )
            )
        elif "combinatorics" in initial_analysis.lower():
            branches = await asyncio.gather(
                self.generate(
                    instruction="Solve using counting principles approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using permutations and combinations approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using probability theory approach...",
                    context=initial_analysis
                )
            )
        else:
            branches = await asyncio.gather(
                self.generate(
                    instruction="Solve using algebraic manipulation approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using calculus techniques approach...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using sequence and series approach...",
                    context=initial_analysis
                )
            )

        # Iterative refinement of each branch
        refined_branches = []
        for branch in branches:
            refined = await self.revise(
                instruction="Critique and improve the solution attempt, focusing on logical consistency, precision, and clarity.",
                context=branch
            )
            refined_branches.append(refined)

        # Ensemble to select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the refined solutions:
            - Select based on completeness and rigor
            - Combine complementary insights if necessary
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_branches
        )

        return final_solution