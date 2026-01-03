# Workflow ID: drop_144_0
# Benchmark: drop
# Data Indices: [162, 48]

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

        # Step 1: Initial Analysis - Extract entities and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - Entities: [names, roles, teams, etc.]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]
            
            Then classify the problem type:
            - Is it numerical, textual, or comparative?
            - What operation(s) are required? (e.g., counting, averaging, extracting spans)
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Fork - Resolve references and identify operations
        reference_resolution, operation_identification = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all pronouns and partial names to specific entities:
                Passage: {self.problem_text}
                Extracted Entities: {initial_analysis}
                
                Provide a mapping of references to entities.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Identify the required operation(s) based on the question:
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                Problem Type: {initial_analysis}
                
                Specify the exact operation(s) needed (e.g., count, sum, average, extract span).""",
                context=initial_analysis
            )
        )

        # Step 3: Processing - Execute operations and validate results
        operation_results = await self.generate(
            instruction=f"""Execute the identified operation(s):
            Operations: {operation_identification}
            Resolved References: {reference_resolution}
            Passage: {self.problem_text}
            
            Show all steps and intermediate results. Validate the final result.""",
            context=f"{reference_resolution}\n{operation_identification}"
        )

        # Step 4: Synthesis - Combine results and select the best answer
        synthesis = await self.ensemble(
            instruction="""Evaluate the results and select the best answer:
            - Does the answer match the expected format?
            - Is the reasoning sound and complete?
            - Are all required operations accounted for?""",
            contexts_list=[initial_analysis, reference_resolution, operation_identification, operation_results]
        )

        # Step 5: Final Validation - Ensure correctness and adherence to format
        final_answer = await self.revise(
            instruction=f"""Validate the final answer:
            Answer: {synthesis}
            Passage: {self.problem_text}
            
            Ensure the answer is exact, matches the expected format, and is fully supported by the passage.""",
            context=synthesis
        )

        return final_answer.strip()