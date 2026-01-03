# Workflow ID: drop_53_0
# Benchmark: drop
# Data Indices: [43, 264]

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

        # Step 1: Initial Analysis - Extract entities and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all relevant entities, numbers, and relationships from the passage. 
            Then classify the question into one of the following types:
            1. Arithmetic (addition, subtraction, etc.)
            2. Counting (tallying occurrences)
            3. Comparison (greater/lesser values)
            4. Span Extraction (exact text spans)
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Processing - Solve based on problem type
        problem_type = await self.generate(
            instruction="Identify the problem type from the initial analysis.",
            context=initial_analysis
        )
        if "arithmetic" in problem_type.lower():
            solution_paths = await asyncio.gather(
                self.generate(
                    instruction="Perform addition/subtraction based on the question.",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Perform multiplication/division if applicable.",
                    context=initial_analysis
                )
            )
        elif "counting" in problem_type.lower():
            solution_paths = await asyncio.gather(
                self.generate(
                    instruction="Count occurrences of specific entities.",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Count distinct entities if applicable.",
                    context=initial_analysis
                )
            )
        elif "comparison" in problem_type.lower():
            solution_paths = await asyncio.gather(
                self.generate(
                    instruction="Compare numerical values to find greater/lesser.",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Compare chronological order if applicable.",
                    context=initial_analysis
                )
            )
        else:  # Span Extraction
            solution_paths = await asyncio.gather(
                self.generate(
                    instruction="Extract exact text spans matching the question.",
                    context=initial_analysis
                )
            )

        # Step 3: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine the solution. Ensure all calculations are correct and complete.",
                context=solution
            ) for solution in solution_paths]
        )

        # Step 4: Synthesis - Merge results and produce final answer
        final_answer = await self.ensemble(
            instruction="Select the best solution or synthesize multiple solutions into a unified answer.",
            contexts_list=refined_solutions
        )

        # Step 5: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction="Check the final answer for correctness and completeness.",
            context=final_answer
        )
        if "error" in validation.lower():
            final_answer = await self.revise(
                instruction=f"Fix issues based on validation: {validation}",
                context=final_answer
            )

        return final_answer