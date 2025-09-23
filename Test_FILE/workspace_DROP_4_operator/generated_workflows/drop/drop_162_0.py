# Workflow ID: drop_162_0
# Benchmark: drop
# Data Indices: [383, 353]

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

        # Step 1: Initial Analysis - Extract Entities and Relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - Are there multiple valid approaches?
            - What's the expected answer format?
            Passage Context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Conditional Branching Based on Classification
        if "numerical" in classification.lower():
            # Numerical problems: Perform arithmetic operations
            operations = await asyncio.gather(
                self.generate(
                    instruction="Perform addition/subtraction based on the question...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Perform counting based on the question...",
                    context=initial_analysis
                )
            )
            result = await self.ensemble(
                instruction="Select the most accurate numerical result...",
                contexts_list=operations
            )
        elif "comparison" in classification.lower():
            # Comparison problems: Determine greater/lesser values or spans
            comparisons = await asyncio.gather(
                self.generate(
                    instruction="Compare values/entities based on the question...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Extract spans for comparison...",
                    context=initial_analysis
                )
            )
            result = await self.ensemble(
                instruction="Select the best comparison result...",
                contexts_list=comparisons
            )
        else:
            # Default approach for other problem types
            result = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=initial_analysis
            )

        # Step 4: Validation and Refinement
        validated_result = await self.revise(
            instruction="Validate the result against expected format and constraints...",
            context=result
        )

        # Step 5: Final Output
        return validated_result