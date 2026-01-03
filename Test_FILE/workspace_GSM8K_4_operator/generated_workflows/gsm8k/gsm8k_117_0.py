# Workflow ID: gsm8k_117_0
# Benchmark: gsm8k
# Data Indices: [289, 165]

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
            instruction="""Extract all numerical values, their relationships, 
            and classify the problem type (e.g., sequential, rate, distribution). 
            Provide a structured breakdown of the problem.""",
            context=""
        )

        # Step 2: Parallel Strategy Generation
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a direct calculation strategy.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a proportion-based strategy.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a multi-step sequential strategy.",
                context=initial_analysis
            )
        )

        # Step 3: Strategy Validation and Selection
        selected_strategy = await self.ensemble(
            instruction="""Evaluate strategies based on clarity, feasibility, 
            and alignment with the problem type. Select the most promising one.""",
            contexts_list=strategies
        )

        # Step 4: Step-by-Step Execution
        intermediate_results = []
        current_context = selected_strategy
        for i in range(8):  # Maximum 8 steps
            step_result = await self.generate(
                instruction=f"""Execute step {i+1} of the selected strategy. 
                Show all calculations and intermediate results. Validate the step.""",
                context=current_context
            )
            revised_step = await self.revise(
                instruction="Check for errors and improve clarity.",
                context=step_result
            )
            intermediate_results.append(revised_step)
            current_context = revised_step

            # Early termination if final answer is reached
            if "final answer" in revised_step.lower():
                break

        # Step 5: Final Verification
        final_verification = await self.revise(
            instruction="""Cross-verify all calculations and ensure the final 
            answer meets the problem's requirements. Present the final answer only.""",
            context="\n".join(intermediate_results)
        )

        # Return the final answer
        return final_verification