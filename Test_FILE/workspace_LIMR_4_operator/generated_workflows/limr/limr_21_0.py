# Workflow ID: limr_21_0
# Benchmark: limr
# Data Indices: [18, 112]

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

        # --- Analysis Phase ---
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (geometry, algebra, combinatorics, etc.)
            - Extract key entities, numbers, and relationships
            - List all constraints and conditions explicitly stated or implied
            - Define the solution space and expected answer format
            Present findings in a structured format.""",
            context=""
        )

        # --- Exploration Phase ---
        strategies = [
            "Solve using algebraic manipulation and equation-solving techniques.",
            "Apply geometric reasoning and relevant theorems.",
            "Use combinatorial enumeration and case analysis.",
            "Employ number-theoretic methods like modular arithmetic and divisibility."
        ]
        exploration_tasks = [
            self.generate(
                instruction=f"Attempt solution using the following strategy: {strategy}",
                context=analysis
            ) for strategy in strategies
        ]
        candidate_solutions = await asyncio.gather(*exploration_tasks)

        # --- Synthesis Phase ---
        synthesis = await self.ensemble(
            instruction="""Evaluate and synthesize the candidate solutions:
            - Assess correctness, elegance, and alignment with constraints
            - Combine complementary insights if applicable
            - Select the most promising solution or derive a new one""",
            contexts_list=candidate_solutions
        )

        # --- Validation Phase ---
        validation = await self.revise(
            instruction="""Validate the synthesized solution:
            - Verify all steps for correctness
            - Ensure it satisfies all constraints and edge cases
            - Refine if necessary to meet precision requirements""",
            context=synthesis
        )

        # Final output
        return validation