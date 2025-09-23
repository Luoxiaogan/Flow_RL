# Workflow ID: drop_156_0
# Benchmark: drop
# Data Indices: [38, 16]

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

        # Initial analysis: Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as structured list with categories.""",
            context=""
        )

        # Reference resolution: Map question references to specific entities
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities in the passage:
            Passage Entities: {initial_analysis}
            Question: [question text]
            Provide a mapping of references to entities.""",
            context=initial_analysis
        )

        # Operation identification: Determine required operations from question phrasing
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question phrasing:
            Passage Entities: {initial_analysis}
            Resolved References: {reference_resolution}
            Question: [question text]
            List the operations needed and their parameters.""",
            context=f"{initial_analysis}

{reference_resolution}"
        )

        # Parallel execution of identified operations
        operations = re.findall(r'Operation: (.+)', operation_identification)
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute the following operation:
                Operation: {op}
                Passage Entities: {initial_analysis}
                Resolved References: {reference_resolution}
                Perform the calculation or extraction and provide the result.""",
                context=f"{initial_analysis}

{reference_resolution}"
            ) for op in operations]
        )

        # Validation and refinement of operation results
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the result of the following operation:
                Operation: {op}
                Result: {res}
                Ensure accuracy and completeness.""",
                context=res
            ) for op, res in zip(operations, operation_results)]
        )

        # Ensemble to synthesize final answer
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the results of all operations into a final answer:
            Operations: {operations}
            Refined Results: {refined_results}
            Format the answer according to the expected output type.""",
            contexts_list=refined_results
        )

        return final_answer