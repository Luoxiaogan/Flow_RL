# Workflow ID: drop_219_0
# Benchmark: drop
# Data Indices: [300, 281]

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

        # Phase 1: Information Extraction and Structuring
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, dates, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Dates: [dates and associated events]
            - Actions: [what happens and when]""",
            context=""
        )
        resolved_entities = await self.revise(
            instruction="""Resolve all references (e.g., pronouns, partial names) to their corresponding entities.
            Ensure all entities are unambiguous and fully resolved.""",
            context=entities
        )

        # Phase 2: Problem Analysis and Operation Identification
        problem_type = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            - Arithmetic: Addition, subtraction, multiplication, division
            - Counting: How many times, how many different
            - Comparison: Greater than, less than, equal to
            - Span Extraction: Exact text span from the passage
            - Multi-step: Requires chaining multiple operations
            
            Based on the following entities and relationships:
            {resolved_entities}""",
            context=""
        )
        constraints = await self.generate(
            instruction=f"""Identify all constraints and conditions from the question:
            - Units (e.g., days, years, meters)
            - Specific entities involved
            - Expected answer format (number, date, text span)""",
            context=problem_type
        )

        # Phase 3: Execution and Validation
        execution_context = f"{resolved_entities}\n{problem_type}\n{constraints}"
        raw_answer = await self.generate(
            instruction="""Execute the identified operation(s) based on the analysis:
            - For arithmetic: Perform precise calculations
            - For counting: Count occurrences or entities
            - For comparison: Evaluate relationships
            - For span extraction: Identify the exact text span
            
            Ensure the result matches the expected format.""",
            context=execution_context
        )
        validated_answer = await self.revise(
            instruction="""Validate the result:
            - Check for correctness
            - Ensure proper formatting
            - Reformat if necessary""",
            context=raw_answer
        )

        # Phase 4: Multi-hop Reasoning and Synthesis (if needed)
        if "multi-step" in problem_type.lower():
            intermediate_results = await asyncio.gather(
                self.generate(
                    instruction="Perform the first operation...",
                    context=execution_context
                ),
                self.generate(
                    instruction="Perform the second operation...",
                    context=execution_context
                )
            )
            final_answer = await self.ensemble(
                instruction="Synthesize intermediate results into a final answer.",
                contexts_list=intermediate_results
            )
        else:
            final_answer = validated_answer

        return final_answer