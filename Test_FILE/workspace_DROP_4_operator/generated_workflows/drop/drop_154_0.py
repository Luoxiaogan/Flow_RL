# Workflow ID: drop_154_0
# Benchmark: drop
# Data Indices: [42, 225]

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

        # Stage 1: Initial Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Stage 2: Question Analysis and Operation Identification
        analysis = await self.generate(
            instruction=f"""Analyze the question and classify it:
            Passage Entities: {entities}
            
            Classify into:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Which is greater/longer, who had more, etc.
            - Span Extraction: Who did, what was the name of, when did, etc.
            
            Identify any references that need resolving and map them to the entities.""",
            context=entities
        )

        # Stage 3: Parallel Processing of Potential Solutions
        if "arithmetic" in analysis.lower():
            solutions = await asyncio.gather(
                self.generate(instruction="Perform addition if applicable...", context=analysis),
                self.generate(instruction="Perform subtraction if applicable...", context=analysis),
                self.generate(instruction="Perform other arithmetic operations if needed...", context=analysis)
            )
        elif "counting" in analysis.lower():
            solutions = await asyncio.gather(
                self.generate(instruction="Count instances explicitly mentioned...", context=analysis),
                self.generate(instruction="Count implied instances based on context...", context=analysis)
            )
        elif "comparison" in analysis.lower():
            solutions = await asyncio.gather(
                self.generate(instruction="Compare values directly...", context=analysis),
                self.generate(instruction="Compare values indirectly using context...", context=analysis)
            )
        else:  # Span Extraction
            solutions = await asyncio.gather(
                self.generate(instruction="Extract exact text spans matching the question...", context=analysis)
            )

        # Stage 4: Ensemble and Validation
        best_solution = await self.ensemble(
            instruction="Select the most plausible solution based on coherence and consistency with the passage.",
            contexts_list=solutions
        )

        final_answer = await self.revise(
            instruction="Ensure the answer matches the expected format (number, date, or exact text span). Revise if necessary.",
            context=best_solution
        )

        return final_answer