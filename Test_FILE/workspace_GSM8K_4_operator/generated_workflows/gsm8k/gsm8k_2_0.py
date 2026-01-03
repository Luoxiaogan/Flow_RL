# Workflow ID: gsm8k_2_0
# Benchmark: gsm8k
# Data Indices: [150, 161]

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

        # Step 1: Initial Analysis - Extract key information and classify problem type
        analysis = await self.generate(
            instruction="""Extract all numerical values, units, entities, and relationships.
            Classify the problem type (e.g., rate, proportion, distribution).
            Identify what the question is asking for.""",
            context=""
        )

        # Step 2: Solution Planning - Generate a structured plan for solving the problem
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a step-by-step plan to solve the problem.
            Include all necessary calculations and intermediate results.""",
            context=analysis
        )

        # Step 3: Parallel Execution - Explore multiple solution paths
        paths = await asyncio.gather(
            self.generate(instruction=f"Solve using direct calculation: {plan}", context=plan),
            self.generate(instruction=f"Solve using proportional reasoning: {plan}", context=plan),
            self.generate(instruction=f"Solve using unit conversion: {plan}", context=plan)
        )

        # Step 4: Validation and Refinement - Validate results and refine as needed
        refined_paths = await asyncio.gather(
            *[self.revise(instruction="Verify calculations and correct errors.", context=path) for path in paths]
        )

        # Step 5: Final Synthesis - Combine insights and output the final answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=refined_paths
        )

        # Output the final numerical answer
        return final_answer.split("####")[-1].strip()