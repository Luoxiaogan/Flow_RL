# Workflow ID: gsm8k_68_0
# Benchmark: gsm8k
# Data Indices: [261, 160]

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
            instruction="""Extract all numerical values, their units, and relationships from the problem. 
            Identify the goal (what is being asked) and classify the problem type (e.g., sequential operations, rate, proportion). 
            Format as structured output with clear labels.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Plans
        plans = await asyncio.gather(
            self.generate(
                instruction="Generate a detailed step-by-step plan focusing on sequential arithmetic operations.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Generate an alternative plan considering potential ambiguities or edge cases.",
                context=initial_analysis
            )
        )

        # Step 3: Select Best Plan Using Ensemble
        selected_plan = await self.ensemble(
            instruction="Evaluate the two plans and select the most logical and complete one. Resolve ambiguities if necessary.",
            contexts_list=plans
        )

        # Step 4: Execute the Selected Plan
        intermediate_results = []
        steps = selected_plan.split("\n")
        for i, step in enumerate(steps):
            result = await self.generate(
                instruction=f"Perform the following step: {step}. Show all calculations and track intermediate results.",
                context="\n".join(intermediate_results)  # Accumulate context
            )
            # Validate and refine the result
            refined_result = await self.revise(
                instruction="Check for correctness, clarity, and consistency. Fix any errors or ambiguities.",
                context=result
            )
            intermediate_results.append(refined_result)

        # Step 5: Validate Final Result
        final_validation = await self.revise(
            instruction="Critique the entire solution process. Ensure all steps are correct and aligned with the problem goal.",
            context="\n".join(intermediate_results)
        )

        # Step 6: Summarize Final Answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution process. Ensure it matches the problem's requirements.",
            context=final_validation
        )

        return final_answer.strip()