# Workflow ID: gsm8k_97_0
# Benchmark: gsm8k
# Data Indices: [15, 152]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Classify the problem type (e.g., sequential operations, rate problem, distribution).
            Identify the target quantity to solve for.
            Format the output as a structured summary.""",
            context=""
        )

        # Step 2: Strategy Formulation
        strategy = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Formulate a high-level plan to solve the problem.
            Consider multiple solution paths if the problem type is ambiguous.
            Output a clear, step-by-step strategy.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration (if needed)
        if "ambiguous" in strategy.lower():
            parallel_strategies = await asyncio.gather(
                self.generate(instruction="Solve using sequential computation.", context=strategy),
                self.generate(instruction="Solve using proportional reasoning.", context=strategy),
                self.generate(instruction="Solve using rate-based calculations.", context=strategy)
            )
            selected_strategy = await self.ensemble(
                instruction="Select the most promising strategy based on clarity and feasibility.",
                contexts_list=parallel_strategies
            )
        else:
            selected_strategy = strategy

        # Step 4: Step-by-Step Execution
        steps = selected_strategy.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            result = await self.generate(
                instruction=f"""Execute step {i+1}:
                {step}
                
                Show all calculations and intermediate results.""",
                context="\n".join(intermediate_results)
            )
            validated_result = await self.revise(
                instruction=f"""Validate the result of step {i+1}.
                Ensure all calculations are correct and units are consistent.""",
                context=result
            )
            intermediate_results.append(validated_result)

        # Step 5: Final Synthesis
        final_answer = await self.generate(
            instruction=f"""Combine all intermediate results to compute the final answer:
            {intermediate_results}
            
            Ensure the output is a single numerical value.""",
            context="\n".join(intermediate_results)
        )

        # Return the final numerical answer
        return final_answer.strip()