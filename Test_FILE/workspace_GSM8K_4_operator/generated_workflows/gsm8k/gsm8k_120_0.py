# Workflow ID: gsm8k_120_0
# Benchmark: gsm8k
# Data Indices: [282, 228]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Extract all numerical values and their units.
            - Identify relationships between quantities.
            - Classify the problem type (e.g., rate, distribution, proportion).
            - Highlight potential ambiguities or missing information.
            Provide the analysis in a structured format.""",
            context=""
        )

        # Phase 2: Solution Strategy Generation
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis:
                {analysis}
                
                Generate a sequential solution strategy:
                - List the steps required to solve the problem.
                - Specify the order of operations.
                - Include intermediate calculations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis:
                {analysis}
                
                Generate an alternative solution strategy:
                - Explore different approaches to solving the problem.
                - Consider edge cases and potential ambiguities.""",
                context=analysis
            )
        )

        # Phase 3: Execution and Validation
        async def execute_strategy(strategy):
            steps = strategy.split("\n")
            results = []
            for step in steps:
                if step.strip():
                    result = await self.generate(
                        instruction=f"""Perform the following calculation:
                        {step}
                        
                        Ensure the result is consistent with the problem context.""",
                        context="\n".join(results)
                    )
                    validated_result = await self.revise(
                        instruction=f"""Validate the calculation:
                        {result}
                        
                        Check for errors or inconsistencies.""",
                        context=result
                    )
                    results.append(validated_result)
            return results

        executions = await asyncio.gather(*[execute_strategy(s) for s in strategies])

        # Phase 4: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the results from multiple strategies:
            - Select the most consistent and accurate solution.
            - Ensure the final answer is numerically exact.
            - Format the answer appropriately.""",
            contexts_list=[f"Strategy {i+1} Results:\n" + "\n".join(e) for i, e in enumerate(executions)]
        )

        return final_answer