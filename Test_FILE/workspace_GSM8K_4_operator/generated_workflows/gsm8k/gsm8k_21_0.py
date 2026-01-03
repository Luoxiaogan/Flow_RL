# Workflow ID: gsm8k_21_0
# Benchmark: gsm8k
# Data Indices: [286, 229]

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

        # Step 1: Initial Analysis - Extract key information and classify problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to extract:
            - All numerical values and their units
            - Relationships between entities
            - Problem type (sequential, rate-based, proportional, etc.)
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve using direct computation. Show all steps.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve using unit conversions and scaling factors if applicable.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve by identifying and resolving interdependencies between variables.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Check and improve each path
        refined_paths = []
        for path in paths:
            validation = await self.revise(
                instruction="Validate this solution for accuracy and consistency.",
                context=path
            )
            if "error" in validation.lower():
                refined_path = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=path
                )
                refined_paths.append(refined_path)
            else:
                refined_paths.append(path)

        # Step 4: Final Synthesis - Select the best solution
        final_solution = await self.ensemble(
            instruction="""Compare all solutions and select the best one based on:
            - Numerical accuracy
            - Logical consistency
            - Alignment with problem requirements""",
            contexts_list=refined_paths
        )

        # Return the final numerical answer
        return final_solution.strip()