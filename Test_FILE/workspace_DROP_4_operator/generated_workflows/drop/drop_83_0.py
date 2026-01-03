# Workflow ID: drop_83_0
# Benchmark: drop
# Data Indices: [487, 389]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names, teams, locations, etc.
            - Numbers: Values and their contexts
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the Question Type
        question_type = await self.generate(
            instruction=f"""Classify the question based on the passage and extracted information:
            {initial_analysis}
            
            Categories:
            1. Arithmetic (addition, subtraction, etc.)
            2. Counting (how many times, how many different, etc.)
            3. Comparison (greater than, less than, etc.)
            4. Span Extraction (who did, what was, etc.)
            5. Multi-step (requires combining multiple facts)
            
            Provide a clear classification and reasoning.""",
            context=initial_analysis
        )

        # Step 3: Dynamic Instruction Generation and Execution
        if "arithmetic" in question_type.lower():
            # Perform arithmetic operations
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operations using the extracted numbers:
                {initial_analysis}
                
                Show all steps and present the final answer.""",
                context=question_type
            )
        elif "counting" in question_type.lower():
            # Count occurrences or entities
            result = await self.generate(
                instruction=f"""Count the required entities or events based on the passage:
                {initial_analysis}
                
                Ensure no instances are missed and provide the count.""",
                context=question_type
            )
        elif "comparison" in question_type.lower():
            # Compare values or attributes
            result = await self.generate(
                instruction=f"""Compare the specified values or attributes:
                {initial_analysis}
                
                Clearly state which is greater, longer, etc., and provide reasoning.""",
                context=question_type
            )
        elif "span extraction" in question_type.lower():
            # Extract exact text spans
            spans = await asyncio.gather(
                self.generate(
                    instruction=f"""Extract the first possible answer span:
                    {initial_analysis}""",
                    context=question_type
                ),
                self.generate(
                    instruction=f"""Extract the second possible answer span:
                    {initial_analysis}""",
                    context=question_type
                )
            )
            result = await self.ensemble(
                instruction="Select the most accurate and complete span.",
                contexts_list=spans
            )
        else:
            # Default multi-step reasoning
            result = await self.generate(
                instruction=f"""Combine multiple facts to answer the question:
                {initial_analysis}
                
                Show all reasoning steps and present the final answer.""",
                context=question_type
            )

        # Step 4: Validation and Refinement
        validation = await self.revise(
            instruction=f"""Validate the result:
            {result}
            
            Check for:
            - Logical consistency
            - Computational accuracy
            - Adherence to expected format
            Provide feedback and suggest improvements if needed.""",
            context=result
        )

        # Step 5: Iterative Refinement (if necessary)
        if "error" in validation.lower() or "improve" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Refine the result based on validation feedback:
                {validation}""",
                context=result
            )
            result = refined_result

        return result