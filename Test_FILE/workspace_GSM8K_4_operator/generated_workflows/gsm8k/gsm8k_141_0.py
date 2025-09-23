# Workflow ID: gsm8k_141_0
# Benchmark: gsm8k
# Data Indices: [243, 269]

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

        # Step 1: Initial Analysis - Extract key information
        initial_analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify all numbers and their units
            - Highlight relationships between quantities
            - Note any constraints or conditions
            - Determine what the question is asking for""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve the problem step-by-step using direct computation.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve the problem using proportional reasoning.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis:
                {initial_analysis}
                
                Solve the problem using rate-based calculations.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Validate and refine each path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution path: {path}",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesis - Combine refined paths into a final solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the refined solution paths into a single, unified answer.
            - Ensure all intermediate steps are valid
            - Confirm the final answer matches the problem's requirements
            - Present the result as a single numerical value""",
            contexts_list=refined_paths
        )

        # Step 5: Final Answer Extraction - Extract the numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the synthesized solution.",
            context=final_solution
        )

        return final_answer.strip()