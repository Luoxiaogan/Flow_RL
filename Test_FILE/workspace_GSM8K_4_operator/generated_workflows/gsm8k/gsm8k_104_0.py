# Workflow ID: gsm8k_104_0
# Benchmark: gsm8k
# Data Indices: [237, 96]

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
            instruction="""Extract all numerical values, identify relationships, and classify the problem type:
            - List all numbers and their context
            - Identify what is being asked
            - Classify the problem (e.g., rate, distribution, proportion)
            Provide structured output.""",
            context=""
        )

        # Step 2: Strategy Selection
        if "rate" in initial_analysis.lower():
            strategy = "rate"
        elif "distribution" in initial_analysis.lower():
            strategy = "distribution"
        else:
            strategy = "general"

        # Step 3: Step-by-Step Solution
        steps = []
        current_context = initial_analysis
        for i in range(8):  # Maximum 8 steps
            step = await self.generate(
                instruction=f"""Perform step {i+1} of the solution:
                - Use the current context: {current_context}
                - Perform the next logical calculation
                - Show intermediate result""",
                context=current_context
            )
            revised_step = await self.revise(
                instruction=f"""Validate step {i+1}:
                - Check calculations
                - Ensure units are correct
                - Add missing details if needed""",
                context=step
            )
            steps.append(revised_step)
            current_context = revised_step

            # Early termination if solution is complete
            if "final answer" in revised_step.lower():
                break

        # Step 4: Parallel Validation
        validations = await asyncio.gather(
            self.generate(instruction="Validate from mathematical perspective", context=current_context),
            self.generate(instruction="Validate from logical perspective", context=current_context),
            self.generate(instruction="Validate from practical perspective", context=current_context)
        )
        validation_synthesis = await self.ensemble(
            instruction="Synthesize validations into unified assessment",
            contexts_list=validations
        )

        # Step 5: Final Output
        final_output = await self.summarize(
            instruction="Extract the final numerical answer with precision",
            context=validation_synthesis
        )

        return final_output