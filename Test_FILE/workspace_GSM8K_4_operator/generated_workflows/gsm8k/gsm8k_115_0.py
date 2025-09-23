# Workflow ID: gsm8k_115_0
# Benchmark: gsm8k
# Data Indices: [104, 223]

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
        
        # Step 1: Extract key information and classify the problem
        analysis = await self.generate(
            instruction="""Analyze the problem and extract key components:
            - Identify all numerical values and their units
            - Determine the relationships between these values
            - Classify the problem type (e.g., sequential operations, rate, distribution, proportions)
            - Identify what the question is asking for
            Provide structured output.""",
            context=""
        )
        
        # Step 2: Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Propose a solution using a sequential chain of operations.",
                context=analysis
            ),
            self.generate(
                instruction="Propose a solution using parallel calculations for independent steps.",
                context=analysis
            ),
            self.generate(
                instruction="Propose a solution using hierarchical decomposition into sub-problems.",
                context=analysis
            )
        )
        
        # Step 3: Evaluate and refine strategies
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this solution strategy. Ensure logical consistency and numerical accuracy.",
                context=strategy
            ) for strategy in strategies]
        )
        
        # Step 4: Select the best strategy
        best_strategy = await self.ensemble(
            instruction="Evaluate these strategies and select the most appropriate one based on clarity, completeness, and correctness.",
            contexts_list=refined_strategies
        )
        
        # Step 5: Execute the solution step-by-step
        solution_steps = await self.generate(
            instruction=f"""Using the selected strategy:
            {best_strategy}
            
            Break the solution into individual steps. Perform calculations sequentially, showing intermediate results.
            Ensure units and context are preserved throughout.""",
            context=best_strategy
        )
        
        # Step 6: Validate and finalize the solution
        final_solution = await self.revise(
            instruction="Verify the calculations and ensure the final answer is numerically exact. Highlight any assumptions or ambiguities.",
            context=solution_steps
        )
        
        # Step 7: Summarize the final result
        summary = await self.summarize(
            instruction="Condense the solution into a single numerical value, preserving units if applicable.",
            context=final_solution
        )
        
        return summary.strip()