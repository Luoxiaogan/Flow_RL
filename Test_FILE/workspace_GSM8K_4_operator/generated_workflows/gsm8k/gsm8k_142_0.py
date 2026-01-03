# Workflow ID: gsm8k_142_0
# Benchmark: gsm8k
# Data Indices: [68, 298]

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

        # Step 1: Analyze problem structure
        analysis = await self.generate(
            instruction="""Extract key information:
            - All numerical values and their units
            - Relationships between entities (e.g., more than, per day)
            - Constraints and conditions
            - What the question is asking for
            Format as a structured list.""",
            context=""
        )

        # Step 2: Explore solution paths in parallel
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Solve using direct calculation.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Solve using proportional scaling.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Solve using unit conversion.""",
                context=analysis
            )
        )

        # Step 3: Select the best solution path
        selected_path = await self.ensemble(
            instruction="Choose the most accurate and complete solution.",
            contexts_list=paths
        )

        # Step 4: Perform sequential calculations
        steps = selected_path.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            if i == 0:
                result = await self.generate(
                    instruction=f"Perform the first calculation: {step}",
                    context=""
                )
            else:
                result = await self.generate(
                    instruction=f"Using the previous result ({intermediate_results[-1]}), perform the next calculation: {step}",
                    context=intermediate_results[-1]
                )
            validated_result = await self.revise(
                instruction="Verify the calculation and improve clarity.",
                context=result
            )
            intermediate_results.append(validated_result)

        # Step 5: Synthesize the final answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the calculations.",
            context="\n".join(intermediate_results)
        )

        return final_answer.strip()