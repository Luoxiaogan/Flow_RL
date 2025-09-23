# Workflow ID: drop_95_0
# Benchmark: drop
# Data Indices: [481, 390]

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

        # Step 1: Parallel Fork for Entity Extraction and Question Analysis
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        question_analysis_task = self.generate(
            instruction="""Analyze the question type and identify required operations:
            - Is it numerical, logical, or textual?
            - Does it involve counting, arithmetic, comparison, or span extraction?
            - What is the expected answer format?""",
            context=""
        )

        # Gather results from parallel tasks
        entities, question_analysis = await asyncio.gather(entities_task, question_analysis_task)

        # Step 2: Merge and Classify Problem Type
        classification = await self.ensemble(
            instruction="""Classify the problem based on:
            - Extracted entities and relationships
            - Question type and required operations
            Determine the solution strategy.""",
            contexts_list=[entities, question_analysis]
        )

        # Step 3: Sequential Chain for Multi-Step Reasoning
        solution_steps = []
        if "arithmetic" in classification.lower():
            arithmetic_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                - Extract relevant numbers from entities: {entities}
                - Apply the required operation (addition, subtraction, etc.)
                - Show all steps and present the final result.""",
                context=classification
            )
            solution_steps.append(arithmetic_result)

        elif "counting" in classification.lower():
            count_result = await self.generate(
                instruction=f"""Count occurrences of specific entities or events:
                - Identify target entities from: {entities}
                - Count their occurrences in the passage
                - Present the total count.""",
                context=classification
            )
            solution_steps.append(count_result)

        elif "span extraction" in classification.lower():
            span_result = await self.generate(
                instruction=f"""Extract exact text spans matching the question:
                - Locate relevant sentences from: {entities}
                - Identify the exact span that answers the question
                - Ensure the span matches the passage exactly.""",
                context=classification
            )
            solution_steps.append(span_result)

        # Step 4: Validation and Refinement
        refined_results = []
        for step in solution_steps:
            validation = await self.revise(
                instruction="Validate and refine the result for accuracy.",
                context=step
            )
            refined_results.append(validation)

        # Step 5: Final Answer Formatting
        final_answer = await self.ensemble(
            instruction="Combine refined results into a single final answer.",
            contexts_list=refined_results
        )

        return final_answer