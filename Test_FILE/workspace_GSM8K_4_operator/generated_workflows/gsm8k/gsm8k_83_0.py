# Workflow ID: gsm8k_83_0
# Benchmark: gsm8k
# Data Indices: [199, 59]

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
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Classify the problem type (e.g., sequential, rate-based, distribution, proportions). 
            Identify what the question is asking for and list any constraints.""",
            context=""
        )
        
        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Develop a solution path focusing on sequential operations. Start with: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution path focusing on proportional relationships. Start with: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution path focusing on rate-based reasoning. Start with: {initial_analysis}",
                context=initial_analysis
            )
        )
        
        # Step 3: Validation Cascade - Validate and refine each solution path
        refined_paths = []
        for path in solution_paths:
            validation = await self.generate(
                instruction=f"Validate the following solution path for correctness and completeness: {path}",
                context=path
            )
            if "error" in validation.lower():
                revised_path = await self.revise(
                    instruction=f"Revise the solution path to fix issues identified: {validation}",
                    context=path
                )
                refined_paths.append(revised_path)
            else:
                refined_paths.append(path)
        
        # Step 4: Synthesis - Combine insights from parallel paths
        synthesis = await self.ensemble(
            instruction="Synthesize the refined solution paths into a unified understanding. Select the most robust approach.",
            contexts_list=refined_paths
        )
        
        # Step 5: Final Output - Summarize reasoning chain and extract numerical answer
        final_summary = await self.summarize(
            instruction="Condense the reasoning chain into a concise summary. Ensure the final numerical answer is clear and exact.",
            context=synthesis
        )
        
        # Return the final numerical answer
        return final_summary.strip()