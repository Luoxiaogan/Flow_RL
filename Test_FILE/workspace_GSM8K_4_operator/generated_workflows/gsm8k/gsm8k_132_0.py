# Workflow ID: gsm8k_132_0
# Benchmark: gsm8k
# Data Indices: [142, 153]

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

        # Initial analysis to decompose the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, their contexts, and relationships:
            - Identify all numbers and what they represent
            - Determine the relationships between these numbers
            - Highlight the question being asked
            Provide a structured breakdown of the problem.""",
            context=""
        )

        # Parallel exploration of different solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction="""Solve the problem using a mathematical approach:
                - Perform calculations step-by-step
                - Track intermediate results
                - Ensure all steps are logically sound""",
                context=initial_analysis
            ),
            self.generate(
                instruction="""Solve the problem using a logical approach:
                - Reason through the problem systematically
                - Use logical deductions to arrive at the solution
                - Validate each deduction against the problem statement""",
                context=initial_analysis
            )
        )

        # Step-by-step calculation and validation for each path
        validated_paths = []
        for path in solution_paths:
            steps = path.split('\n')
            validated_steps = []
            for step in steps:
                calculation = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    Ensure the result is accurate and track intermediate results.""",
                    context="\n".join(validated_steps)
                )
                validation = await self.revise(
                    instruction="""Validate the calculation:
                    - Check for errors
                    - Ensure logical consistency
                    - Verify against the problem statement""",
                    context=calculation
                )
                if "error" in validation.lower():
                    revised_calculation = await self.revise(
                        instruction=f"""Revise the calculation based on the following feedback:
                        {validation}
                        Correct any mistakes and ensure accuracy.""",
                        context=calculation
                    )
                    validated_steps.append(revised_calculation)
                else:
                    validated_steps.append(calculation)
            validated_paths.append("\n".join(validated_steps))

        # Final synthesis to extract the answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the results from different solution paths:
            - Compare the final answers from each path
            - Select the most accurate and reliable result
            - Present the final answer as a single numerical value""",
            contexts_list=validated_paths
        )

        return final_answer