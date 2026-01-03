# Workflow ID: drop_123_0
# Benchmark: drop
# Data Indices: [250, 263]

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

        # Step 1: Initial Analysis
        entity_extraction = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and required operations:
            - Is it numerical, logical, or textual?
            - Does it involve counting, arithmetic, comparison, or span extraction?
            - Identify key phrases indicating the required operation(s).""",
            context=""
        )

        # Step 2: Reference Resolution
        reference_resolution = await self.generate(
            instruction=f"""Resolve pronouns and partial references in the question:
            Passage entities: {entity_extraction}
            Map all references to specific entities in the passage.""",
            context=question_analysis
        )

        # Step 3: Operation Identification and Execution
        operation_execution = await self.generate(
            instruction=f"""Based on the question analysis:
            Question type: {question_analysis}
            Resolved references: {reference_resolution}
            
            Perform the required operation(s):
            - For arithmetic, locate relevant numbers and perform the operation.
            - For counting, iterate through the passage and count occurrences.
            - For comparison, evaluate relationships between entities or values.
            - For span extraction, locate and extract the exact text span.""",
            context=f"{entity_extraction}

{reference_resolution}"
        )

        # Step 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the intermediate results:
            Operation results: {operation_execution}
            
            Ensure they align with the question's requirements and resolve any ambiguities.""",
            context=operation_execution
        )

        refined_results = await self.revise(
            instruction=f"""Refine the results based on validation feedback:
            Validation: {validation}""",
            context=operation_execution
        )

        # Step 5: Final Answer Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the results into a single coherent answer:
            Refined results: {refined_results}
            
            Ensure the final answer matches the expected format (number, date, or exact text span).""",
            contexts_list=[entity_extraction, reference_resolution, refined_results]
        )

        return final_answer