# Workflow ID: gsm8k_24_0
# Benchmark: gsm8k
# Data Indices: [294, 264]

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
            instruction="""Analyze the problem:
            - Extract all numerical values and their units.
            - Identify relationships between quantities.
            - Classify the problem type (e.g., rate, distribution, proportion).
            - Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Problem Classification - Determine the solution approach
        classification = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Classify the problem into one of the following categories:
            1. Sequential Operations
            2. Rate Problems
            3. Distribution
            4. Proportions
            5. Multi-entity Tracking
            
            Provide a detailed explanation of the classification.""",
            context=initial_analysis
        )

        # Step 3: Build Solution Strategies - Generate multiple approaches
        strategies = await asyncio.gather(
            self.generate(instruction="Develop a direct solution strategy.", context=classification),
            self.generate(instruction="Develop an alternative solution strategy.", context=classification)
        )

        # Step 4: Ensemble Best Strategy - Select the most promising approach
        best_strategy = await self.ensemble(
            instruction="Evaluate and select the most robust solution strategy.",
            contexts_list=strategies
        )

        # Step 5: Execute Solution - Perform calculations step-by-step
        solution_steps = []
        current_context = best_strategy
        for step in range(8):  # Maximum 8 steps
            step_result = await self.generate(
                instruction=f"""Execute the next step in the solution:
                Current Context: {current_context}
                
                Perform the calculation and provide intermediate results.""",
                context=current_context
            )
            solution_steps.append(step_result)
            current_context = step_result

            # Validate intermediate result
            validation = await self.revise(
                instruction="Check the accuracy and consistency of the intermediate result.",
                context=step_result
            )
            if "error" in validation.lower():
                revised_step = await self.revise(
                    instruction=f"Correct the error: {validation}",
                    context=step_result
                )
                solution_steps[-1] = revised_step
                current_context = revised_step

        # Step 6: Synthesize Final Answer - Combine all steps into a single result
        final_answer = await self.generate(
            instruction=f"""Combine all solution steps into the final answer:
            Steps: {solution_steps}
            
            Provide the final numerical value only.""",
            context="\n".join(solution_steps)
        )

        return final_answer.strip()