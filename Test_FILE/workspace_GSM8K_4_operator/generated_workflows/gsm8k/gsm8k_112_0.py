# Workflow ID: gsm8k_112_0
# Benchmark: gsm8k
# Data Indices: [189, 20]

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
            instruction="""Extract all key components from the problem:
            - Named entities (people, objects, etc.)
            - Numerical values and their units
            - Relationships between entities
            - Problem type (rate, distribution, proportion, etc.)
            - Implicit constraints or assumptions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Identify Calculation Steps
        calculation_steps = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Identify the sequence of calculations needed to solve the problem:
            - List each step explicitly
            - Specify inputs, operations, and outputs
            - Track units throughout""",
            context=initial_analysis
        )

        # Step 3: Execute Calculations
        steps = calculation_steps.split("\n")
        results = []
        for i, step in enumerate(steps):
            result = await self.generate(
                instruction=f"""Perform the following calculation:
                {step}
                
                Show all intermediate results and track units.""",
                context="\n".join(results)  # Pass accumulated context
            )
            # Validate the result
            validated = await self.revise(
                instruction=f"""Validate the calculation:
                - Check arithmetic correctness
                - Ensure unit consistency
                - Verify logical coherence""",
                context=result
            )
            results.append(validated)

        # Step 4: Synthesize Final Answer
        final_answer = await self.ensemble(
            instruction="""Combine all validated results into a final answer:
            - Ensure consistency across steps
            - Present the answer in the required format (numerical value only)""",
            contexts_list=results
        )

        return final_answer.strip()