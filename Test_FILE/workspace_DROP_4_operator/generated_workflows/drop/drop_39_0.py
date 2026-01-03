# Workflow ID: drop_39_0
# Benchmark: drop
# Data Indices: [186, 163]

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

        # Stage 1: Initial Analysis - Problem Decomposition
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Extract all named entities, numbers, and relationships.
            2. Classify the question type (e.g., arithmetic, comparison, span extraction).
            3. Identify constraints and conditions.
            Format as structured list with categories:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [actions and events]""",
            context=""
        )

        # Stage 2: Parallel Exploration - Multiple Perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction=f"Directly extract answer from passage using: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Infer answer by combining related facts: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Perform required calculations: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Stage 3: Validation and Refinement
        synthesized_solution = await self.ensemble(
            instruction="Synthesize perspectives into a unified solution. Resolve conflicts and ensure consistency.",
            contexts_list=perspectives
        )

        refined_solution = await self.revise(
            instruction="Validate and refine the solution. Fix errors, add missing details, and ensure correctness.",
            context=synthesized_solution
        )

        # Stage 4: Final Synthesis
        final_answer = await self.summarize(
            instruction="Condense the solution into a concise, well-formatted answer. Match expected output format.",
            context=refined_solution
        )

        return final_answer