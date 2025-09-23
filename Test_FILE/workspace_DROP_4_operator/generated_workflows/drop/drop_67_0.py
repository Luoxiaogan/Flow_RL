# Workflow ID: drop_67_0
# Benchmark: drop
# Data Indices: [375, 493]

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
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Reference Resolution - Resolve ambiguous terms
        resolved_references = await self.revise(
            instruction=f"""Resolve ambiguous references in the passage:
            - Map pronouns to named entities
            - Clarify partial names or vague terms
            Passage Context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Operation Identification - Determine required operations
        operation_identification = await self.generate(
            instruction=f"""Identify the operations required to answer the question:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            Passage Context: {resolved_references}""",
            context=resolved_references
        )

        # Step 4: Parallel Solution Paths - Generate multiple candidate solutions
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using direct extraction:
                Passage Context: {resolved_references}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Solve the problem using step-by-step reasoning:
                Passage Context: {resolved_references}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Solve the problem using numerical computation:
                Passage Context: {resolved_references}""",
                context=resolved_references
            )
        )

        # Step 5: Validation and Refinement - Check and refine solutions
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                - Ensure consistency with the passage
                - Match the expected answer format
                Solution Context: {solution}""",
                context=solution
            ) for solution in solution_paths]
        )

        # Step 6: Final Synthesis - Select the best solution
        final_answer = await self.ensemble(
            instruction="""Select the best solution:
            - Most consistent with the passage
            - Matches the expected format
            - Logically sound""",
            contexts_list=validated_solutions
        )

        return final_answer