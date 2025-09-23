# Workflow ID: gsm8k_28_0
# Benchmark: gsm8k
# Data Indices: [163, 18]

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

        # Step 1: Extract key information and identify solution paths
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Identify what is being asked and outline potential solution paths. 
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"Attempt solution using direct calculations: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Attempt solution using proportional reasoning: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Attempt solution using iterative refinement: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Revise and validate each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Check for errors and improve clarity. Ensure all steps are logically sound.",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 4: Summarize each refined solution
        summarized_solutions = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the solution into key points and final answer.",
                context=solution
            ) for solution in refined_solutions]
        )

        # Step 5: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="Compare solutions and select the most accurate and complete one. Resolve any ambiguities.",
            contexts_list=summarized_solutions
        )

        # Step 6: Extract the final numerical answer
        match = re.search(r"(\d+\.?\d*)", final_solution)
        final_answer = float(match.group(1)) if match else None

        return final_answer