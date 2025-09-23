# Workflow ID: drop_173_0
# Benchmark: drop
# Data Indices: [361, 84]

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
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question to classify its type
        question_analysis_task = self.generate(
            instruction="""Classify the question type and identify key phrases:
            - Is it numerical, logical, or textual?
            - What operation is required? (e.g., addition, subtraction, comparison)
            - What is the expected answer format?""",
            context=""
        )

        # Run both tasks in parallel
        entities, question_analysis = await asyncio.gather(entities_task, question_analysis_task)

        # Step 3: Map references in the question to entities in the passage
        reference_mapping = await self.generate(
            instruction=f"""Resolve pronouns and partial references in the question to specific entities in the passage:
            Passage Entities: {entities}
            Question Analysis: {question_analysis}""",
            context=f"{entities}

{question_analysis}"
        )

        # Step 4: Determine the required operation
        operation_plan = await self.generate(
            instruction=f"""Based on the extracted entities and question analysis, determine the exact operation required:
            Entities: {entities}
            Question Analysis: {question_analysis}
            Reference Mapping: {reference_mapping}""",
            context=f"{entities}

{question_analysis}

{reference_mapping}"
        )

        # Step 5: Execute the operation
        raw_answer = await self.generate(
            instruction=f"""Perform the required operation using the provided context:
            Entities: {entities}
            Question Analysis: {question_analysis}
            Reference Mapping: {reference_mapping}
            Operation Plan: {operation_plan}""",
            context=f"{entities}

{question_analysis}

{reference_mapping}

{operation_plan}"
        )

        # Step 6: Validate and refine the result
        validated_answer = await self.revise(
            instruction="""Validate the result against the expected format:
            - Ensure numbers are accurate
            - Ensure text spans match the passage exactly
            - Correct any discrepancies""",
            context=raw_answer
        )

        # Step 7: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Condense the final answer into the required format.",
            context=validated_answer
        )

        return final_answer