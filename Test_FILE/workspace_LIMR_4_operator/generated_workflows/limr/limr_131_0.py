# Workflow ID: limr_131_0
# Benchmark: limr
# Data Indices: [37, 160]

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
        
        # Step 1: Classify the problem to determine the appropriate approach
        classification = await self.generate(
            instruction="""Classify this problem:
            1. Identify the primary mathematical discipline (geometry, algebra, etc.)
            2. Determine if it requires exact calculation or heuristic estimation
            3. Highlight any special techniques or theorems that might apply
            Provide a structured classification with reasoning.""",
            context=""
        )
        
        # Step 2: Generate multiple initial solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Based on classification: {classification}\nDevelop a direct computation approach...",
                context=""
            ),
            self.generate(
                instruction=f"Based on classification: {classification}\nDevelop a creative transformation approach...",
                context=""
            ),
            self.generate(
                instruction=f"Based on classification: {classification}\nDevelop a heuristic estimation approach...",
                context=""
            )
        )
        
        # Step 3: Ensemble to select the most promising strategy
        selected_strategy = await self.ensemble(
            instruction="Evaluate and select the most promising solution strategy based on feasibility and accuracy.",
            contexts_list=strategies
        )
        
        # Step 4: Iteratively refine the selected strategy
        refined_solution = selected_strategy
        for _ in range(3):  # Limit iterations to prevent excessive computation
            validation = await self.generate(
                instruction="Validate the current solution and identify areas for improvement.",
                context=refined_solution
            )
            if "error" in validation.lower() or "improvement" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Refine the solution based on validation: {validation}",
                    context=refined_solution
                )
            else:
                break
        
        # Step 5: Summarize the final solution
        final_summary = await self.summarize(
            instruction="Condense the refined solution into a clear, concise summary with the final answer.",
            context=refined_solution
        )
        
        return final_summary