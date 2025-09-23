# Workflow ID: gsm8k_85_0
# Benchmark: gsm8k
# Data Indices: [103, 277]

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

        # Step 1: Initial Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Sequential Operations: Step-by-step calculations building on previous results.
            - Rate Problems: Involving distance/speed/time, work rates, or unit prices.
            - Distribution: Dividing quantities, equal sharing, or handling remainders.
            - Proportions: Percentages, fractions, ratios, or scaling.
            - Multi-entity: Tracking different quantities for multiple people/objects.
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction=f"""Based on the classification:
            {analysis}
            
            Decompose the problem into sub-problems. Each sub-problem should correspond to an intermediate computation.
            Format as a numbered list with clear descriptions of what each sub-problem entails.""",
            context=analysis
        )

        # Step 3: Parallel Computation of Sub-Problems
        sub_problems = decomposition.split("\n")
        sub_problem_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the following sub-problem:
                {sub_problem}
                
                Show all calculations and intermediate results.""",
                context=decomposition
            ) for sub_problem in sub_problems if sub_problem.strip()]
        )

        # Step 4: Iterative Refinement and Validation
        refined_results = []
        for result in sub_problem_results:
            validation = await self.generate(
                instruction=f"""Validate the following computation:
                {result}
                
                Check for arithmetic errors, logical consistency, and alignment with the problem's requirements.""",
                context=result
            )
            if "error" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Revise the computation to fix the following issues:
                    {validation}""",
                    context=result
                )
                refined_results.append(revised)
            else:
                refined_results.append(result)

        # Step 5: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the intermediate results into a final answer.
            Ensure the answer is numerically exact and formatted correctly.""",
            contexts_list=refined_results
        )

        return final_answer