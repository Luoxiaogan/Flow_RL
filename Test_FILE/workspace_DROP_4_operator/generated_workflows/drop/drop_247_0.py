# Workflow ID: drop_247_0
# Benchmark: drop
# Data Indices: [305, 180]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and their relationships from the passage and question:
            - Entities: Names, teams, events, etc.
            - Numbers: Quantities, dates, scores, etc.
            - Relationships: How entities and numbers are connected
            Resolve pronouns and partial names to specific entities.""",
            context=""
        )

        # Step 2: Problem Classification - Identify problem type and required operations
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {initial_analysis}
            
            Categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/less, longer/shorter, etc.)
            - Span Extraction (who, what, when, etc.)
            - Multi-step (requires chaining multiple operations)
            
            Output the category and describe the required operations.""",
            context=initial_analysis
        )

        # Step 3: Parallel Processing - Execute operations based on classification
        if "arithmetic" in classification.lower():
            # Extract numbers and perform arithmetic operations
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage and question:
                {initial_analysis}
                
                Perform the required arithmetic operations (addition, subtraction, etc.) and provide intermediate results.""",
                context=classification
            )
            results = await asyncio.gather(
                self.generate(instruction="Calculate sum of relevant numbers...", context=numbers),
                self.generate(instruction="Calculate difference of relevant numbers...", context=numbers)
            )
            final_result = await self.ensemble(
                instruction="Select the correct arithmetic result based on the question...",
                contexts_list=results
            )
        elif "counting" in classification.lower():
            # Count occurrences of specific entities or events
            counts = await self.generate(
                instruction=f"""Count occurrences of relevant entities or events:
                {initial_analysis}
                
                Provide counts for each entity/event mentioned in the question.""",
                context=classification
            )
            final_result = await self.revise(
                instruction="Validate counts and ensure they match the question requirements...",
                context=counts
            )
        elif "comparison" in classification.lower():
            # Compare two or more entities/events based on specific criteria
            comparisons = await asyncio.gather(
                self.generate(instruction="Compare entities based on quantity...", context=classification),
                self.generate(instruction="Compare entities based on time/duration...", context=classification)
            )
            final_result = await self.ensemble(
                instruction="Select the correct comparison result based on the question...",
                contexts_list=comparisons
            )
        elif "span extraction" in classification.lower():
            # Extract exact text spans matching the question
            spans = await self.generate(
                instruction=f"""Extract exact text spans from the passage that answer the question:
                {initial_analysis}
                
                Ensure spans match the expected format (names, dates, etc.).""",
                context=classification
            )
            final_result = await self.revise(
                instruction="Validate extracted spans and ensure they match the question requirements...",
                context=spans
            )
        else:
            # Default multi-step processing
            steps = await asyncio.gather(
                self.generate(instruction="Identify first step in reasoning...", context=classification),
                self.generate(instruction="Identify second step in reasoning...", context=classification)
            )
            final_result = await self.ensemble(
                instruction="Synthesize multi-step reasoning into final answer...",
                contexts_list=steps
            )

        # Step 4: Validation and Refinement - Ensure accuracy and correctness
        validated_result = await self.revise(
            instruction="Validate the final result against the original problem and refine if necessary...",
            context=final_result
        )

        # Step 5: Output Formatting - Format the final answer
        formatted_answer = await self.summarize(
            instruction="Condense the final result into the required format (number, date, text span)...",
            context=validated_result
        )

        return formatted_answer