# Workflow ID: mbppplus_170_0
# Benchmark: mbppplus
# Data Indices: [162, 187]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        
        # Phase 1: Problem Decomposition and Understanding
        # Break down the problem into its fundamental components
        decomposition_task = self.decompose(
            instruction="""Systematically decompose this programming problem into its atomic components. For each component, identify:
            1. Input specification: What data types and structures are provided? What are their constraints?
            2. Output specification: What should be returned? What data type and format is expected?
            3. Transformation pattern: What operation or algorithm bridges input to output? 
            4. Edge cases: What boundary conditions, empty inputs, or special values must be handled?
            5. Test case patterns: What do the example test cases reveal about expected behavior?
            Return this as a structured analysis that can guide code generation.""",
            context=""
        )
        
        # Phase 2: Parallel Solution Strategy Generation
        # Generate three different approaches simultaneously
        literal_approach = self.generate(
            instruction="""Generate a literal, straightforward implementation that directly mirrors the test cases shown. 
            Focus on simplicity and direct translation of requirements. Assume the most common case and implement the minimal 
            solution that would pass the basic tests. Don't over-engineer, but ensure correct data types and basic edge cases.""",
            context=""
        )
        
        abstract_approach = self.generate(
            instruction="""Generate an abstract, general solution that focuses on the underlying algorithmic pattern rather than 
            specific test cases. Identify the core computational concept (sorting, filtering, transformation, etc.) and implement 
            a clean, reusable version that would work for any valid input. Prioritize elegance and algorithmic correctness.""",
            context=""
        )
        
        defensive_approach = self.generate(
            instruction="""Generate a defensive, robust implementation that anticipates and handles all possible edge cases. 
            Include explicit checks for empty inputs, single elements, boundary conditions, and type validation. Prioritize 
            correctness over simplicity, ensuring the solution will work for any input within the problem's domain.""",
            context=""
        )
        
        # Execute decomposition and parallel generation concurrently
        decomposition, literal_code, abstract_code, defensive_code = await asyncio.gather(
            decomposition_task,
            literal_approach,
            abstract_approach,
            defensive_approach
        )
        
        # Phase 3: Synthesize the best aspects of each approach
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three candidate solutions into a single optimal implementation. Consider:
            - Take the simplicity and directness from the literal approach
            - Incorporate the algorithmic elegance from the abstract approach
            - Integrate the robustness and edge case handling from the defensive approach
            - Ensure the final solution matches the exact function signature and return type specified
            - Preserve any particularly clever or efficient code patterns from any of the approaches
            Return only the final Python function implementation with necessary imports.""",
            contexts_list=[literal_code, abstract_code, defensive_code]
        )
        
        # Phase 4: Validation and Iterative Refinement
        # Test the synthesized solution against the problem's requirements
        validation_result = await self.programmer(
            instruction=f"""Execute the following code and validate it against the problem requirements. 
            The code must:
            1. Match the exact function signature specified in the problem
            2. Handle all edge cases identified in the decomposition: {decomposition}
            3. Return the correct data type and format
            4. Pass basic functionality tests (simulate the test cases mentioned in the problem)
            If any issues are found, return detailed error messages specifying what failed and how to fix it.
            If no issues are found, return 'VALID: Solution meets all requirements'.""",
            context=synthesized_solution,
            max_retries=1
        )
        
        # If validation fails, revise based on feedback
        if "VALID:" not in validation_result:
            refined_solution = await self.revise(
                instruction=f"""Revise the implementation to fix the issues identified in validation: {validation_result}
                Specifically address:
                - Any failed test cases or edge cases
                - Data type mismatches or return format errors
                - Algorithmic flaws or logical errors
                - Performance or efficiency concerns
                Maintain the core approach while correcting the specific problems identified.
                Return only the corrected Python function implementation.""",
                context=synthesized_solution
            )
            final_solution = refined_solution
        else:
            final_solution = synthesized_solution
        
        # Phase 5: Final cleanup and formatting
        # Ensure the solution is clean, properly formatted, and matches requirements exactly
        cleaned_solution = await self.revise(
            instruction="""Final cleanup pass: Ensure the code is properly formatted, follows Python best practices, 
            and exactly matches the required function signature. Remove any unnecessary comments, imports, or code. 
            Verify that the solution handles edge cases appropriately and returns the correct data type. 
            The output should be ONLY the function implementation with necessary imports, nothing else.""",
            context=final_solution
        )
        
        return cleaned_solution