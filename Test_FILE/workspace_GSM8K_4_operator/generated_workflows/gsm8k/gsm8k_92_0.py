# Workflow ID: gsm8k_92_0
# Benchmark: gsm8k
# Data Indices: [27, 97]

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

        # Step 1: Extract entities and classify the problem
        entities = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Classify the problem type (e.g., sequential, rate, proportion, distribution). 
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Identify constraints and solution strategies
        constraints = await self.generate(
            instruction=f"""Given the entities: {entities}
            Identify all constraints and conditions. Define the solution space and outline potential strategies.""",
            context=entities
        )

        # Step 3: Generate parallel solution paths
        parallel_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a sequential approach: 
                {entities} and {constraints}""",
                context=constraints
            ),
            self.generate(
                instruction=f"""Solve the problem using a proportional reasoning approach: 
                {entities} and {constraints}""",
                context=constraints
            ),
            self.generate(
                instruction=f"""Solve the problem using a rate-based approach: 
                {entities} and {constraints}""",
                context=constraints
            )
        )

        # Step 4: Synthesize parallel solutions
        synthesized_solution = await self.ensemble(
            instruction="Synthesize the best solution from the parallel approaches.",
            contexts_list=parallel_solutions
        )

        # Step 5: Iterative refinement
        refined_solution = synthesized_solution
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"Validate the solution: {refined_solution}",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final answer extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from the refined solution: 
            {refined_solution}. Ensure the answer is exact and formatted correctly.""",
            context=refined_solution
        )

        return final_answer