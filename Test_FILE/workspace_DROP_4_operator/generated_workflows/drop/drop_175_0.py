# Workflow ID: drop_175_0
# Benchmark: drop
# Data Indices: [154, 235]

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

        # Step 1: Extract entities and numbers
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references and refine entities
        refined_entities = await self.revise(
            instruction="""Resolve pronouns and partial names to specific entities:
            Ensure all references are consistent and unambiguous.""",
            context=entities_and_numbers
        )

        # Step 3: Classify problem type and identify operations
        classification_tasks = await asyncio.gather(
            self.generate(
                instruction="""Classify the problem type:
                - Is it numerical, logical, or textual?
                - Does it involve addition, subtraction, counting, or comparison?
                - What is the expected answer format?""",
                context=refined_entities
            ),
            self.generate(
                instruction="""Identify potential solution strategies:
                - What operations are required?
                - What are the key steps to solve the problem?""",
                context=refined_entities
            )
        )
        problem_classification = classification_tasks[0]
        solution_strategies = classification_tasks[1]

        # Step 4: Choose the best strategy based on classification
        chosen_strategy = await self.ensemble(
            instruction="""Select the most appropriate solution strategy:
            - Consider the problem type and required operations.
            - Ensure the strategy aligns with the expected answer format.""",
            contexts_list=classification_tasks
        )

        # Step 5: Execute the chosen strategy
        solution = await self.generate(
            instruction=f"""Execute the solution strategy:
            Strategy: {chosen_strategy}
            Use the following entities and numbers: {refined_entities}
            Perform the required operations and provide the final answer.""",
            context=refined_entities
        )

        # Step 6: Validate and refine the solution
        validation = await self.generate(
            instruction="""Validate the solution:
            - Are all steps logically sound?
            - Are calculations accurate?
            - Does the answer match the expected format?""",
            context=solution
        )
        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                Feedback: {validation}""",
                context=solution
            )
            solution = refined_solution

        # Step 7: Format the final answer
        final_answer = await self.summarize(
            instruction="""Condense the solution into the final answer:
            - Include only the essential information.
            - Ensure the format matches the expected answer.""",
            context=solution
        )

        return final_answer