# Workflow ID: drop_197_0
# Benchmark: drop
# Data Indices: [283, 334]

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

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Identify the type of question (arithmetic, counting, comparison, span extraction). 
            Resolve references to ensure clarity. Format the output as a structured list.""",
            context=""
        )

        # Step 2: Operation Identification
        operation_type = await self.generate(
            instruction=f"""Based on the question and the following decomposition:
            {decomposition}
            
            Determine the required operation(s): arithmetic, counting, comparison, or span extraction. 
            Provide a clear classification and justification.""",
            context=decomposition
        )

        # Conditional Branch: Handle Different Operation Types
        if "arithmetic" in operation_type.lower():
            # Parallel execution for arithmetic operations
            calculations = await asyncio.gather(
                self.generate(
                    instruction=f"""Perform addition or subtraction based on the question:
                    {operation_type}
                    
                    Use the following data:
                    {decomposition}""",
                    context=decomposition
                ),
                self.generate(
                    instruction=f"""Verify the calculations by re-evaluating the numbers:
                    {operation_type}
                    
                    Use the following data:
                    {decomposition}""",
                    context=decomposition
                )
            )
            result = await self.ensemble(
                instruction="Select the most accurate calculation.",
                contexts_list=calculations
            )
        elif "comparison" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Compare the relevant values based on the question:
                {operation_type}
                
                Use the following data:
                {decomposition}""",
                context=decomposition
            )
        elif "span extraction" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question:
                {operation_type}
                
                Use the following data:
                {decomposition}""",
                context=decomposition
            )
        else:
            # Default handling for other operation types
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                {operation_type}
                
                Use the following data:
                {decomposition}""",
                context=decomposition
            )

        # Step 3: Iterative Refinement
        for _ in range(3):  # Allow up to 3 iterations for refinement
            refined_result = await self.revise(
                instruction=f"""Refine the result for accuracy and clarity:
                Current result: {result}
                
                Ensure the answer matches the expected format.""",
                context=result
            )
            if refined_result == result:  # Convergence check
                break
            result = refined_result

        # Step 4: Final Answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer to match the expected output:
            Current result: {result}
            
            Ensure numerical answers are precise and include units if necessary. 
            Verify that text spans match the passage exactly.""",
            context=result
        )

        return final_answer