# Workflow ID: drop_121_0
# Benchmark: drop
# Data Indices: [178, 116]

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

        # Step 1: Extract key information from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Identify the required operation(s) from the question
        operation_analysis = await self.generate(
            instruction=f"""Analyze the question and determine the required operation(s):
            - Is it numerical (counting, addition, subtraction, etc.)?
            - Does it involve comparison?
            - Is it a span extraction task?
            - What is the expected answer format?
            Entities and numbers from the passage: {entities}""",
            context=entities
        )

        # Step 3: Execute operations in parallel
        if "count" in operation_analysis.lower():
            count_task = self.generate(
                instruction=f"""Count the occurrences of relevant entities or events:
                Entities and numbers from the passage: {entities}""",
                context=entities
            )
        else:
            count_task = None

        if "compare" in operation_analysis.lower():
            compare_task = self.generate(
                instruction=f"""Compare relevant entities or numbers:
                Entities and numbers from the passage: {entities}""",
                context=entities
            )
        else:
            compare_task = None

        if "extract" in operation_analysis.lower():
            extract_task = self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Entities and numbers from the passage: {entities}""",
                context=entities
            )
        else:
            extract_task = None

        # Gather results from parallel tasks
        tasks = [task for task in [count_task, compare_task, extract_task] if task]
        results = await asyncio.gather(*tasks)

        # Step 4: Synthesize results into a unified answer
        synthesized_answer = await self.ensemble(
            instruction="""Synthesize results into a unified answer:
            - Combine counts, comparisons, and extracted spans as needed
            - Ensure the answer matches the expected format""",
            contexts_list=results
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction="""Validate the answer:
            - Check if it matches the expected format
            - Ensure all references are resolved
            - Correct any errors or ambiguities""",
            context=synthesized_answer
        )

        return refined_answer