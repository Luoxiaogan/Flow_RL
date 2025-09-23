# Workflow ID: drop_243_0
# Benchmark: drop
# Data Indices: [62, 446]

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
        
        # Step 1: Extract entities and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        reference_resolution = await self.generate(
            instruction=f"""Resolve all references in the passage:
            - Map pronouns and partial names to specific entities
            - Ensure clarity and accuracy
            Given entities: {entities_extraction}""",
            context=entities_extraction
        )
        
        # Step 2: Classify problem type and identify operations
        problem_classification = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            - Arithmetic (addition, subtraction, counting)
            - Comparison (greater/less, longest/shortest)
            - Span extraction (who did..., what was...)
            Identify required operations and their sequence.
            Passage: {self.problem_text}
            Resolved references: {reference_resolution}""",
            context=reference_resolution
        )
        
        # Step 3: Perform required operations
        if "arithmetic" in problem_classification.lower():
            calculations = await asyncio.gather(
                self.generate(instruction="Perform addition calculations...", context=problem_classification),
                self.generate(instruction="Perform subtraction calculations...", context=problem_classification),
                self.generate(instruction="Perform counting calculations...", context=problem_classification)
            )
            operation_results = await self.ensemble(
                instruction="Combine arithmetic results into final calculation",
                contexts_list=calculations
            )
        elif "comparison" in problem_classification.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Generate candidate answers for comparison...", context=problem_classification),
                self.generate(instruction="Generate alternative candidate answers...", context=problem_classification)
            )
            operation_results = await self.ensemble(
                instruction="Select the best candidate answer based on criteria",
                contexts_list=candidates
            )
        else:  # Span extraction
            operation_results = await self.generate(
                instruction="Extract exact text span matching the question...",
                context=problem_classification
            )
        
        # Step 4: Validate and refine results
        validation = await self.generate(
            instruction=f"""Validate the intermediate results:
            - Check accuracy and completeness
            - Identify any missing details or errors
            Intermediate results: {operation_results}""",
            context=operation_results
        )
        
        refined_results = await self.revise(
            instruction="Refine results based on validation feedback...",
            context=validation
        )
        
        # Step 5: Generate final answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer according to expected output type:
            - Number only
            - Date format
            - Exact text span
            Refined results: {refined_results}""",
            context=refined_results
        )
        
        return final_answer