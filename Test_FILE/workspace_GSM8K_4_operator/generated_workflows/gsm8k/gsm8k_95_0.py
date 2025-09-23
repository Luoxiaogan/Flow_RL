# Workflow ID: gsm8k_95_0
# Benchmark: gsm8k
# Data Indices: [80, 238]

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

        # Step 1: Extract key information and understand the question
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, their context, and relationships. 
            Identify what the problem is asking for. Provide structured output with:
            - Numbers and their meanings
            - Relationships between entities
            - The target answer format""",
            context=""
        )

        # Step 2: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}. "
                            "Develop a detailed step-by-step solution focusing on arithmetic operations.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}. "
                            "Explore alternative solution approaches, considering different interpretations.",
                context=initial_analysis
            )
        )

        # Step 3: Validate and refine each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Verify calculations, ensure logical consistency, and improve clarity.",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Summarize intermediate results for synthesis
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the solution into key steps and intermediate results.",
                context=path
            ) for path in refined_paths]
        )

        # Step 5: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution. Resolve any discrepancies.",
            contexts_list=summaries
        )

        # Step 6: Extract the final numerical answer
        final_answer = await self.generate(
            instruction=f"From the final solution: {final_solution}, extract the numerical answer only.",
            context=final_solution
        )

        return final_answer.strip()