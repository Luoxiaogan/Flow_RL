# Workflow ID: gsm8k_128_0
# Benchmark: gsm8k
# Data Indices: [186, 293]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the problem:
            - Identify named entities (people, objects, etc.)
            - Extract numerical values and their units
            - Determine relationships between entities and numbers
            - Classify the problem type (e.g., sequential operations, rate problem, distribution)
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Solution Paths - Generate multiple approaches
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct arithmetic operations:
                Problem context: {initial_analysis}
                - Perform step-by-step calculations
                - Show intermediate results
                - Validate against problem constraints""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using proportional reasoning:
                Problem context: {initial_analysis}
                - Identify proportional relationships
                - Perform scaling or unit conversion
                - Validate against problem constraints""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using alternative methods:
                Problem context: {initial_analysis}
                - Explore unconventional approaches
                - Validate against problem constraints""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Check and refine paths
        refined_paths = []
        for path in solution_paths:
            validation = await self.generate(
                instruction=f"""Validate this solution path:
                Path: {path}
                - Check intermediate results
                - Ensure consistency with problem constraints
                - Identify errors or ambiguities""",
                context=path
            )
            if "error" not in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine this solution path:
                    Path: {path}
                    Validation: {validation}
                    - Improve clarity and precision
                    - Add missing details""",
                    context=path
                )
                refined_paths.append(refined)

        # Step 4: Synthesis and Decision - Select the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined paths:
            - Evaluate accuracy and robustness
            - Select the most complete and precise solution""",
            contexts_list=refined_paths
        )

        # Step 5: Final Answer Extraction - Extract the numerical answer
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer:
            Solution: {final_solution}
            - Ensure the answer is a single numerical value
            - Include units if applicable""",
            context=final_solution
        )

        return final_answer