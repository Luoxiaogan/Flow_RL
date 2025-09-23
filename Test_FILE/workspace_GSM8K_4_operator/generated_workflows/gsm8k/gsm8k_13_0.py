# Workflow ID: gsm8k_13_0
# Benchmark: gsm8k
# Data Indices: [208, 271]

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

        # Step 1: Initial Analysis - Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Extract all numerical values and their units
            - Identify relationships between quantities
            - Classify the problem type (e.g., sequential, rate-based, proportional)
            - Determine what the question is asking for
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Solution Strategy Selection - Choose an approach based on classification
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Select a solution strategy:
            - For sequential problems, outline step-by-step calculations
            - For rate-based problems, identify relevant formulas (e.g., distance = speed × time)
            - For proportional problems, determine scaling factors or ratios
            Provide a detailed plan.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Generate multiple solution paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using the primary strategy:
                {strategy}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Explore an alternative approach:
                {strategy}""",
                context=initial_analysis
            )
        )

        # Step 4: Validation and Refinement - Validate paths and refine results
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Check calculations, ensure logical consistency, and refine if needed.",
                context=path
            ) for path in paths]
        )

        # Step 5: Ensemble Decision - Select the best solution
        final_solution = await self.ensemble(
            instruction="Compare solutions, select the most accurate and complete one.",
            contexts_list=refined_paths
        )

        # Step 6: Final Answer Extraction - Extract the numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return final_answer.strip()