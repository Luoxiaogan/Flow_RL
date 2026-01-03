# Workflow ID: limr_50_0
# Benchmark: limr
# Data Indices: [205, 195]

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

        # Step 1: Initial Analysis - Decompose the problem into sub-problems
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the main components (geometric, algebraic, combinatorial, etc.)
            - Extract all given data, constraints, and relationships
            - Classify the problem type and suggest potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution based on: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Refinement - Critique and improve each approach
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this approach. Highlight strengths, weaknesses, and areas for improvement.",
                context=approach
            ) for approach in approaches]
        )

        # Step 4: Summarization - Condense insights from each approach
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Summarize the key insights and solution steps from this approach.",
                context=refined_approach
            ) for refined_approach in refined_approaches]
        )

        # Step 5: Ensemble Evaluation - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate the summarized approaches and determine the best solution:
            - Consider accuracy, completeness, and alignment with the problem's constraints
            - Synthesize insights from multiple approaches if necessary""",
            contexts_list=summaries
        )

        # Step 6: Validation - Verify the final solution
        validation = await self.generate(
            instruction=f"""Validate the final solution:
            - Check all intermediate steps for correctness
            - Ensure the solution meets the problem's constraints
            - Cross-check with alternative methods if possible""",
            context=final_solution
        )

        # Step 7: Final Output - Present the solution in the required format
        result = await self.revise(
            instruction="""Format the final solution as an integer between 000 and 999:
            - Ensure the answer is precise and meets the problem's requirements
            - Include any necessary explanations or justifications""",
            context=validation
        )

        return result