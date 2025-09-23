# Workflow ID: drop_19_0
# Benchmark: drop
# Data Indices: [387, 70]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify the question
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Then classify the question into one of the following categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was, etc.)
            Provide a structured output with clear labels.""",
            context=""
        )

        # Step 2: Reference Resolution - Resolve pronouns and partial names
        resolved_references = await self.revise(
            instruction="""Resolve all ambiguous references in the question to specific entities in the passage. 
            For example, map 'they' to a specific team or player. Ensure all references are unambiguous.""",
            context=initial_analysis
        )

        # Step 3: Operation Identification - Identify required operations
        operation_candidates = await asyncio.gather(
            self.generate(
                instruction="Interpret the question as an arithmetic operation (e.g., addition, subtraction).",
                context=resolved_references
            ),
            self.generate(
                instruction="Interpret the question as a counting task (e.g., how many times, how many different).",
                context=resolved_references
            ),
            self.generate(
                instruction="Interpret the question as a comparison task (e.g., greater than, less than).",
                context=resolved_references
            ),
            self.generate(
                instruction="Interpret the question as a span extraction task (e.g., who did, what was).",
                context=resolved_references
            )
        )
        selected_operation = await self.ensemble(
            instruction="Select the most appropriate interpretation of the question based on clarity and relevance.",
            contexts_list=operation_candidates
        )

        # Step 4: Multi-hop Reasoning - Execute the identified operation
        intermediate_results = await self.generate(
            instruction=f"""Based on the selected operation:
            {selected_operation}
            
            Perform the required calculations or reasoning steps. For multi-hop reasoning, 
            compute intermediate results and combine them appropriately.""",
            context=resolved_references
        )

        # Step 5: Validation and Formatting - Ensure the answer matches the expected format
        final_answer = await self.revise(
            instruction="""Validate the solution against the expected format:
            - For numerical answers, ensure they are non-negative and match constraints.
            - For span extraction, ensure the text matches the passage exactly.
            - For dates or structured outputs, format them correctly.
            Refine the solution if necessary.""",
            context=intermediate_results
        )

        return final_answer