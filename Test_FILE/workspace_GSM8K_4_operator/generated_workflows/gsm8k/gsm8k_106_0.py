# Workflow ID: gsm8k_106_0
# Benchmark: gsm8k
# Data Indices: [75, 132]

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

        # Step 1: Extract key information and propose solution paths
        initial_analysis = await self.generate(
            instruction="""Identify all numerical values, units, and relationships in the problem. 
            Propose multiple solution paths, considering different interpretations of the problem.""",
            context=""
        )

        # Step 2: Generate parallel solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(instruction="Develop a detailed solution based on the first interpretation.", context=initial_analysis),
            self.generate(instruction="Develop a detailed solution based on the second interpretation.", context=initial_analysis),
            self.generate(instruction="Develop a detailed solution based on the third interpretation.", context=initial_analysis)
        )

        # Step 3: Validate and refine each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Check the solution for logical consistency and numerical accuracy. Correct any errors and improve clarity.",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 4: Summarize intermediate results
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Summarize the key findings and intermediate results. Highlight any assumptions or ambiguities.",
                context=solution
            ) for solution in refined_solutions]
        )

        # Step 5: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Compare the refined solutions and select the most accurate and complete one. Resolve any discrepancies.",
            contexts_list=summaries
        )

        # Step 6: Iterative refinement (if needed)
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate the final solution for correctness and completeness.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix issues identified in validation: {validation}",
                    context=final_solution
                )
            else:
                break

        return final_solution