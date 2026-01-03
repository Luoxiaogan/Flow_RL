# Workflow ID: drop_65_0
# Benchmark: drop
# Data Indices: [258, 400]

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

        # Step 1: Extract all named entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the problem type and identify required operations
        problem_type = await self.generate(
            instruction=f"""Classify this problem based on the question and extracted entities:
            {entities}
            
            Determine:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What operation(s) are needed? (e.g., addition, subtraction, comparison, span extraction)
            - What is the expected answer format? (number, date, text span)""",
            context=entities
        )

        # Step 3: Build cumulative context
        cumulative_context = f"{entities}\n\n{problem_type}"

        # Step 4: Parallel exploration for multi-hop reasoning
        if "comparison" in problem_type.lower() or "multi-hop" in problem_type.lower():
            parallel_results = await asyncio.gather(
                self.generate(
                    instruction=f"""Analyze the first entity/path:
                    {cumulative_context}""",
                    context=cumulative_context
                ),
                self.generate(
                    instruction=f"""Analyze the second entity/path:
                    {cumulative_context}""",
                    context=cumulative_context
                )
            )
            synthesized_result = await self.ensemble(
                instruction="Synthesize results from parallel analyses into a unified answer",
                contexts_list=parallel_results
            )
            cumulative_context += f"\n\n{synthesized_result}"

        # Step 5: Iterative refinement
        for _ in range(3):  # Limit iterations to avoid excessive computation
            validation = await self.generate(
                instruction=f"""Validate the current solution:
                {cumulative_context}""",
                context=cumulative_context
            )
            if "error" in validation.lower():
                cumulative_context = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    {validation}""",
                    context=cumulative_context
                )
            else:
                break

        # Step 6: Format the final answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer based on the expected format:
            {cumulative_context}""",
            context=cumulative_context
        )

        return final_answer