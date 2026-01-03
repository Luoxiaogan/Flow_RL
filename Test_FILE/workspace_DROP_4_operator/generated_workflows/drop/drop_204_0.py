# Workflow ID: drop_204_0
# Benchmark: drop
# Data Indices: [74, 248]

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

        # Phase 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract key information from the passage:
            - Named entities (people, places, organizations)
            - Numbers and their contexts (e.g., percentages, ages)
            - Classify the problem type (arithmetic, counting, comparison, span extraction)
            Provide structured output.""",
            context=""
        )

        # Phase 2: Contextual Refinement
        refined_context = await self.revise(
            instruction="""Resolve references and clarify relationships:
            - Map pronouns to specific entities
            - Clarify ambiguous terms
            - Ensure all entities and numbers are correctly linked""",
            context=initial_analysis
        )

        # Phase 3: Solution Execution
        problem_type = await self.generate(
            instruction="Identify the problem type from the refined context.",
            context=refined_context
        )

        if "arithmetic" in problem_type.lower():
            solution = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Use numbers and contexts from: {refined_context}
                - Show all steps and calculations
                - Present the final result""",
                context=refined_context
            )
        elif "counting" in problem_type.lower():
            solution = await self.generate(
                instruction=f"""Count occurrences of the specified entity or pattern:
                - Use entities and numbers from: {refined_context}
                - Ensure all instances are counted
                - Present the total count""",
                context=refined_context
            )
        elif "comparison" in problem_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Evaluate the first value...", context=refined_context),
                self.generate(instruction="Evaluate the second value...", context=refined_context)
            )
            solution = await self.ensemble(
                instruction="Compare the two values and determine the correct answer.",
                contexts_list=candidates
            )
        elif "span extraction" in problem_type.lower():
            solution = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                - Use entities and numbers from: {refined_context}
                - Ensure the span matches the passage exactly""",
                context=refined_context
            )
        else:
            solution = await self.generate(
                instruction="Solve the problem using general reasoning.",
                context=refined_context
            )

        # Phase 4: Validation and Output
        validated_solution = await self.revise(
            instruction="Verify the solution matches the expected format and is accurate.",
            context=solution
        )
        final_answer = await self.summarize(
            instruction="Condense the solution into a concise answer.",
            context=validated_solution
        )

        return final_answer