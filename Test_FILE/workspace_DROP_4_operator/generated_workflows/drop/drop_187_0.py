# Workflow ID: drop_187_0
# Benchmark: drop
# Data Indices: [119, 20]

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
        import re

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all relevant information from the passage:
            - Entities (people, places, organizations)
            - Numbers and their context
            - Relationships between entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Question Classification - Identify the question type and required operations
        question_classification = await self.generate(
            instruction=f"""Classify the question based on the extracted information:
            {initial_analysis}
            
            Determine:
            - Is it numerical, logical, or textual?
            - Does it involve addition, subtraction, counting, comparison, or span extraction?
            - What is the expected answer format?""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using arithmetic operations:
                {question_classification}
                
                Identify numbers and perform calculations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using counting:
                {question_classification}
                
                Count instances of specific entities or events.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using span extraction:
                {question_classification}
                
                Extract exact text spans matching the question.""",
                context=initial_analysis
            )
        )

        # Step 4: Operation Execution - Execute the identified operations
        executed_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                {strategy}
                
                Ensure calculations are correct and spans match exactly.""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 5: Final Synthesis - Select or synthesize the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best answer or synthesize from multiple options:
            - Match the expected format (number, date, or exact span)
            - Ensure consistency with the passage and question
            - Resolve ambiguities by selecting the most plausible option.""",
            contexts_list=executed_strategies
        )

        # Step 6: Format Validation - Ensure the answer matches the expected format
        formatted_answer = await self.revise(
            instruction="""Format the final answer:
            - If numerical, remove any non-numeric characters
            - If a span, ensure it matches the passage exactly
            - If ambiguous, select the simplest valid option.""",
            context=final_answer
        )

        return formatted_answer.strip()