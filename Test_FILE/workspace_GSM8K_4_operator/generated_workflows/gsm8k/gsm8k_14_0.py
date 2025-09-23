# Workflow ID: gsm8k_14_0
# Benchmark: gsm8k
# Data Indices: [51, 56]

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
            instruction="""Extract all numerical values, entities, and relationships:
            - List all numbers and their contexts
            - Identify problem type (e.g., sequential operations, rate problems)
            - Highlight constraints and conditions""",
            context=""
        )

        # Step 2: Solution Planning
        solution_plan = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Create a high-level solution plan:
            - Sequence of operations
            - Intermediate goals
            - Expected answer format""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration
        parallel_results = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct computation:
                Plan: {solution_plan}
                Show all steps and intermediate results.""",
                context=solution_plan
            ),
            self.generate(
                instruction=f"""Solve using unit-based reasoning:
                Plan: {solution_plan}
                Track units throughout calculations.""",
                context=solution_plan
            )
        )

        # Step 4: Iterative Refinement
        refined_results = []
        for result in parallel_results:
            refined = await self.revise(
                instruction="Validate and improve this solution. Correct errors and clarify ambiguities.",
                context=result
            )
            refined_results.append(refined)

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution. Ensure numerical precision.",
            contexts_list=refined_results
        )

        final_answer = await self.summarize(
            instruction="Extract the final numerical answer. Format as a single value.",
            context=final_solution
        )

        return final_answer.strip()