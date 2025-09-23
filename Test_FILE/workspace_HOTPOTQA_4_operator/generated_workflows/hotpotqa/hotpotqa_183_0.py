# Workflow ID: hotpotqa_183_0
# Benchmark: hotpotqa
# Data Indices: [430, 405]

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

        # Initial Analysis: Identify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Extract all named entities, numbers, and relationships.
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Parallel Exploration: Generate multiple reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted entities: {initial_analysis}
                Build a reasoning chain for a bridge question.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted entities: {initial_analysis}
                Build a reasoning chain for a comparison question.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted entities: {initial_analysis}
                Build a reasoning chain for a compositional question.""",
                context=initial_analysis
            )
        )

        # Synthesis: Select the best reasoning path
        best_path = await self.ensemble(
            instruction="Evaluate and select the most plausible reasoning chain.",
            contexts_list=reasoning_paths
        )

        # Refinement Loop: Iteratively improve the solution
        refined_solution = best_path
        for _ in range(3):
            validation = await self.generate(
                instruction=f"Validate the reasoning chain: {refined_solution}",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the refined reasoning chain: {refined_solution}
            Ensure the answer is a short text span or yes/no response.""",
            context=refined_solution
        )

        return final_answer