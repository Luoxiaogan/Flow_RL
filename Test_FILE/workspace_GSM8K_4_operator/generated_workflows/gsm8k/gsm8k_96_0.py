# Workflow ID: gsm8k_96_0
# Benchmark: gsm8k
# Data Indices: [284, 203]

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

        # Step 1: Initial Extraction
        extraction = await self.generate(
            instruction="""Extract all key components from the problem:
            - Numbers and their units
            - Entities (people, objects, etc.)
            - Relationships and constraints
            - What is being asked for
            Format as a structured list.""",
            context=""
        )

        # Step 2: Path Generation
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using extracted components: {extraction}
                Solve using a sequential calculation approach.
                Show all intermediate steps.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Using extracted components: {extraction}
                Solve using a proportional reasoning approach.
                Show all intermediate steps.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Using extracted components: {extraction}
                Solve using a rate-based reasoning approach.
                Show all intermediate steps.""",
                context=extraction
            )
        )

        # Step 3: Iterative Refinement
        refined_paths = []
        for path in paths:
            refined = await self.revise(
                instruction="Verify calculations, clarify reasoning, and correct errors.",
                context=path
            )
            refined_paths.append(refined)

        # Step 4: Context Accumulation
        cumulative_context = "\n".join(refined_paths)
        summary = await self.summarize(
            instruction="Condense key findings and intermediate results into a concise summary.",
            context=cumulative_context
        )

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction="Select the most consistent and complete solution.",
            contexts_list=refined_paths
        )

        return final_solution