# Workflow ID: gsm8k_146_0
# Benchmark: gsm8k
# Data Indices: [242, 173]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Numerical values and their context (units, relationships).
            - Entities involved (people, objects).
            - Actions or operations described.
            - Constraints or conditions (explicit or implicit).
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        direct_calculation = self.generate(
            instruction=f"""Solve the problem step-by-step using the extracted information:
            {initial_analysis}
            Follow the problem's narrative and perform calculations sequentially.
            Show all intermediate results.""",
            context=initial_analysis
        )
        alternative_perspective = self.generate(
            instruction=f"""Reinterpret the problem using alternative methods:
            {initial_analysis}
            Consider proportions, rates, or other mathematical relationships.
            Show all intermediate results.""",
            context=initial_analysis
        )
        validation_path = self.generate(
            instruction=f"""Validate the assumptions and constraints:
            {initial_analysis}
            Check for feasibility and logical consistency.
            Highlight any issues or ambiguities.""",
            context=initial_analysis
        )

        # Execute parallel tasks
        results = await asyncio.gather(direct_calculation, alternative_perspective, validation_path)

        # Step 3: Refinement
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction="Correct errors, clarify reasoning, and ensure precision.",
                context=result
            ) for result in results]
        )

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the results from multiple approaches:
            - Ensure consistency across solutions.
            - Select the most accurate and logically coherent result.
            - Resolve any discrepancies.""",
            contexts_list=refined_results
        )

        # Step 5: Summarize Final Output
        final_answer = await self.summarize(
            instruction="Condense the solution into a single numerical value.",
            context=final_solution
        )

        return final_answer