# Workflow ID: gsm8k_111_0
# Benchmark: gsm8k
# Data Indices: [257, 239]

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

        # Phase 1: Problem Analysis and Decomposition
        analysis = await self.generate(
            instruction="""Extract all numerical values, their context, and relationships:
            - List all numbers and what they represent.
            - Identify operations needed (e.g., fractions, rates, proportions).
            - Determine the sequence of calculations.""",
            context=""
        )

        # Phase 2: Sequential Calculation Chain
        steps = analysis.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            if "operation" in step.lower():
                operation = await self.generate(
                    instruction=f"""Perform the following operation: {step}
                    Use previous results if applicable.""",
                    context="\n".join(intermediate_results)
                )
                validated_operation = await self.revise(
                    instruction="Check for errors and improve clarity.",
                    context=operation
                )
                intermediate_results.append(validated_operation)

        # Phase 3: Adaptive Refinement
        if len(intermediate_results) > 1:
            candidates = await asyncio.gather(
                *[self.generate(
                    instruction=f"Explore alternative solution for step {i+1}",
                    context=step
                ) for i, step in enumerate(intermediate_results)]
            )
            refined_solution = await self.ensemble(
                instruction="Select the most accurate solution.",
                contexts_list=candidates
            )
            intermediate_results.append(refined_solution)

        # Phase 4: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the completed calculation chain.",
            context="\n".join(intermediate_results)
        )

        return final_answer.strip()