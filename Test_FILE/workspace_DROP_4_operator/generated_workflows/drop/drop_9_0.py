# Workflow ID: drop_9_0
# Benchmark: drop
# Data Indices: [65, 411]

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

        # Step 1: Extract entities and numbers from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as structured list.""",
            context=""
        )

        # Step 2: Parse the question and identify the required operation
        operation = await self.generate(
            instruction=f"""Analyze the question and determine the required operation:
            Passage entities: {entities}
            Identify:
            - Operation type (counting, comparison, arithmetic, span extraction)
            - References to entities in the passage
            - Expected answer format""",
            context=entities
        )

        # Step 3: Generate candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using numerical reasoning:
                Entities: {entities}
                Operation: {operation}
                Perform calculations and provide result.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Solve using textual reasoning:
                Entities: {entities}
                Operation: {operation}
                Extract relevant text spans and provide result.""",
                context=entities
            )
        )

        # Step 4: Synthesize and validate the final answer
        final_answer = await self.ensemble(
            instruction="""Evaluate candidate solutions:
            - Select the most accurate and complete answer
            - Ensure the format matches the expected output
            - Resolve any conflicts or ambiguities""",
            contexts_list=candidates
        )

        # Step 5: Iterative refinement (if needed)
        if "ambiguous" in final_answer.lower() or "unclear" in final_answer.lower():
            refined_answer = await self.revise(
                instruction="Clarify and refine the answer based on earlier analysis.",
                context=final_answer
            )
            return refined_answer

        return final_answer