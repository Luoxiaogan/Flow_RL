# Workflow ID: drop_27_0
# Benchmark: drop
# Data Indices: [49, 407]

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

        # Step 1: Initial Analysis - Extract entities and numbers
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Question Analysis - Parse the question
        question_analysis_task = self.generate(
            instruction="""Analyze the question:
            - Identify the operation(s) required (counting, arithmetic, comparison, span extraction)
            - Resolve references (pronouns, partial names)
            - Determine the expected answer format (number, date, text span)""",
            context=""
        )

        # Run extraction and question analysis in parallel
        entities, question_analysis = await asyncio.gather(entities_task, question_analysis_task)

        # Step 3: Operation Execution - Dynamically select and execute the operation
        if "count" in question_analysis.lower():
            result = await self.generate(
                instruction=f"""Count the relevant instances based on:
                Entities: {entities}
                Question Analysis: {question_analysis}""",
                context=f"{entities}

{question_analysis}"
            )
        elif "difference" in question_analysis.lower() or "more" in question_analysis.lower():
            result = await self.generate(
                instruction=f"""Perform subtraction based on:
                Entities: {entities}
                Question Analysis: {question_analysis}""",
                context=f"{entities}

{question_analysis}"
            )
        elif "longest" in question_analysis.lower() or "greatest" in question_analysis.lower():
            result = await self.generate(
                instruction=f"""Identify the maximum value based on:
                Entities: {entities}
                Question Analysis: {question_analysis}""",
                context=f"{entities}

{question_analysis}"
            )
        else:
            result = await self.generate(
                instruction=f"""Extract the exact text span based on:
                Entities: {entities}
                Question Analysis: {question_analysis}""",
                context=f"{entities}

{question_analysis}"
            )

        # Step 4: Answer Formatting - Ensure the answer matches the expected format
        formatted_answer = await self.revise(
            instruction=f"""Format the answer to match the expected output:
            Result: {result}
            Expected Format: {question_analysis}""",
            context=result
        )

        return formatted_answer