# Workflow ID: gsm8k_144_0
# Benchmark: gsm8k
# Data Indices: [61, 184]

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

        # Step 1: Analyze the problem structure
        analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem.
            Identify the question being asked and classify the problem type (e.g., sequential operations, rate problem).
            Format the output as structured text.""",
            context=""
        )

        # Step 2: Determine the solution strategy
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Determine the sequence of operations required to solve the problem.
            Provide detailed instructions for each step.""",
            context=analysis
        )

        # Step 3: Generate multiple hypotheses if ambiguity is detected
        if "ambiguity" in analysis.lower():
            hypotheses = await asyncio.gather(
                self.generate(instruction="Solve assuming interpretation A...", context=strategy),
                self.generate(instruction="Solve assuming interpretation B...", context=strategy)
            )
        else:
            hypotheses = [strategy]

        # Step 4: Execute the solution strategy
        results = []
        for hypothesis in hypotheses:
            result = await self.generate(
                instruction=f"""Execute the solution strategy step by step:
                {hypothesis}""",
                context=""
            )
            # Validate intermediate results
            validation = await self.generate(
                instruction="Check for logical consistency and numerical correctness.",
                context=result
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction="Correct errors and refine the solution.",
                    context=result
                )
                results.append(refined)
            else:
                results.append(result)

        # Step 5: Synthesize multiple solutions if necessary
        if len(results) > 1:
            final_solution = await self.ensemble(
                instruction="Select the most plausible solution based on logical consistency and numerical correctness.",
                contexts_list=results
            )
        else:
            final_solution = results[0]

        # Step 6: Extract the final answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return final_answer