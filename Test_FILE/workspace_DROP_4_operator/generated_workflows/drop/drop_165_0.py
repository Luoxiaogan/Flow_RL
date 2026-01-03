# Workflow ID: drop_165_0
# Benchmark: drop
# Data Indices: [223, 442]

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

        # Phase 1: Initial Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Phase 2: Question Classification and Operation Identification
        question_analysis = await self.generate(
            instruction=f"""Classify the question type and identify required operations.
            Passage Entities: {entities}
            
            Question Types:
            - Arithmetic: Addition, subtraction, multiplication, division
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, equal to, etc.
            - Span Extraction: Who did, what was, when did, etc.
            - Multi-step: Requires chaining multiple operations or facts
            
            Identify the specific operation(s) needed to solve the question.""",
            context=entities
        )

        # Phase 3: Contextual Mapping and Reference Resolution
        reference_mapping = await self.generate(
            instruction=f"""Map question references to specific entities in the passage.
            Passage Entities: {entities}
            Question Analysis: {question_analysis}
            
            Resolve pronouns and partial names to their corresponding entities.""",
            context=question_analysis
        )

        # Phase 4: Operation Execution
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform arithmetic operations if required.
                Passage Entities: {entities}
                Question Analysis: {question_analysis}
                Reference Mapping: {reference_mapping}
                
                Ensure precise calculations and maintain full precision.""",
                context=reference_mapping
            ),
            self.generate(
                instruction=f"""Perform counting operations if required.
                Passage Entities: {entities}
                Question Analysis: {question_analysis}
                Reference Mapping: {reference_mapping}
                
                Count instances accurately and ensure no duplicates.""",
                context=reference_mapping
            ),
            self.generate(
                instruction=f"""Perform comparison operations if required.
                Passage Entities: {entities}
                Question Analysis: {question_analysis}
                Reference Mapping: {reference_mapping}
                
                Compare values and determine relationships.""",
                context=reference_mapping
            ),
            self.generate(
                instruction=f"""Perform span extraction if required.
                Passage Entities: {entities}
                Question Analysis: {question_analysis}
                Reference Mapping: {reference_mapping}
                
                Extract exact text spans that match the question.""",
                context=reference_mapping
            )
        )

        # Phase 5: Validation and Refinement
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the result.
                Original Result: {result}
                
                Check for errors, inconsistencies, and ensure the answer matches the expected format.""",
                context=result
            ) for result in operation_results]
        )

        # Phase 6: Final Answer Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer from multiple candidate solutions.
            Refined Results: {refined_results}
            
            Select the most accurate and consistent answer.""",
            contexts_list=refined_results
        )

        return final_answer