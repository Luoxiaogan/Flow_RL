# Workflow ID: gsm8k_123_0
# Benchmark: gsm8k
# Data Indices: [162, 71]

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

        # Step 1: Initial Analysis - Extract key information and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Identify what is being asked and classify the problem type (e.g., sequential operations, rate problem). 
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}, solve the problem step-by-step.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}, solve the problem using proportions and ratios.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}, solve the problem using unit analysis.",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Critique and improve each path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution path: {path}. Check for logical consistency and accuracy.",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Summarization - Condense each path to its essential components
        summarized_paths = await asyncio.gather(
            *[self.summarize(
                instruction=f"Summarize this solution path: {path}. Focus on key steps and final result.",
                context=path
            ) for path in refined_paths]
        )

        # Step 5: Ensemble - Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Compare these solution paths and synthesize the most accurate and complete answer. Resolve any contradictions.",
            contexts_list=summarized_paths
        )

        # Return the final numerical answer
        return final_solution