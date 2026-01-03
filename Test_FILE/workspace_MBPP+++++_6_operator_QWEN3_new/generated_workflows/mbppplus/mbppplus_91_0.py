# Workflow ID: mbppplus_91_0
# Benchmark: mbppplus
# Data Indices: [51, 40]

import asyncio

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
        import json

        # Phase 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. Classify problem type: mathematical formula, data transformation, string manipulation, logical validation, or other.
            2. Identify exact input/output data types and structures (lists, tuples, sets, strings, numbers).
            3. Extract all explicit and implicit constraints and edge cases (empty inputs, single elements, duplicates, boundary values).
            4. Determine if solution requires exact computation, approximation, or heuristic approach.
            5. Note any domain-specific knowledge required (e.g., number theory, matrix operations).
            6. Specify expected return format and type consistency requirements.
            Present analysis as structured JSON with keys: problem_type, input_spec, output_spec, constraints, approach_type, domain_knowledge, format_requirements.""",
            context=""
        )

        # Phase 2: Structured Specification Decomposition
        decomposition = await self.decompose(
            instruction="""Based on the classification, decompose the problem into:
            - Core algorithmic primitive (what fundamental operation is needed?)
            - Data flow specification (input → transformations → output)
            - Validation criteria (what tests must the solution pass?)
            - Error handling requirements (how to handle invalid inputs?)
            - Performance constraints (time/space complexity if relevant)
            Return as list of subproblems with dependencies.""",
            context=classification
        )

        # Phase 3: Parallel Solution Strategy Generation
        solution_strategies = await asyncio.gather(
            # Strategy 1: Direct Programmer Implementation
            self.programmer(
                instruction=f"""Implement solution based on this specification:
                {classification}
                
                Requirements:
                - Match exact function signature from problem
                - Handle all edge cases identified in classification
                - Return correct data type as specified
                - Include necessary imports
                - No wrapper functions or classes
                - Code must be production-ready and robust""",
                context="",
                max_retries=3
            ),
            
            # Strategy 2: Algorithmic Description → Code
            self.generate(
                instruction="""First, describe the solution algorithm in natural language:
                - Step-by-step procedure
                - Key operations and transformations
                - Edge case handling strategy
                - Data type management
                Then, based on this description, generate the Python implementation.""",
                context=classification
            ),
            
            # Strategy 3: Iterative Refinement from Naive Solution
            self.revise(
                instruction="""Start with simplest possible solution, then iteratively improve:
                1. First pass: Basic implementation ignoring edge cases
                2. Second pass: Add edge case handling and type safety
                3. Third pass: Optimize and add comments for clarity
                Return final refined version.""",
                context=await self.generate(
                    instruction="Create naive initial solution ignoring edge cases",
                    context=classification
                )
            )
        )

        # Phase 4: Ensemble Selection with Quality Gates
        best_solution = await self.ensemble(
            instruction="""Select best solution based on:
            1. Correctness: Matches problem requirements and handles edge cases
            2. Robustness: Graceful error handling and type safety
            3. Efficiency: Reasonable time/space complexity
            4. Readability: Clear, well-structured code
            5. Completeness: Includes all necessary imports and matches signature
            Return only the selected code implementation, nothing else.""",
            contexts_list=solution_strategies
        )

        # Phase 5: Adversarial Validation Loop
        for attempt in range(3):
            # Generate edge case tests
            edge_cases = await self.generate(
                instruction=f"""Generate comprehensive test cases including:
                - Empty inputs
                - Single element inputs
                - Boundary values
                - Invalid/malformed inputs
                - Maximum/minimum values
                - Duplicate elements
                - Type mismatches
                Format as Python assert statements testing the solution.""",
                context=f"Classification: {classification}\nSolution: {best_solution}"
            )
            
            # Validate solution against edge cases
            validation_result = await self.programmer(
                instruction=f"""Test the solution against these edge cases:
                {edge_cases}
                
                Return 'PASSED' if all tests pass, otherwise return detailed error messages.""",
                context=best_solution,
                max_retries=1
            )
            
            if "PASSED" in validation_result:
                break
            else:
                # Revise solution based on failures
                best_solution = await self.revise(
                    instruction=f"""Fix the following issues identified in testing:
                    {validation_result}
                    
                    Requirements:
                    - Maintain original function signature
                    - Preserve core algorithm
                    - Add specific fixes for failed test cases
                    - Ensure type safety and edge case handling
                    Return revised implementation.""",
                    context=best_solution
                )

        # Phase 6: Final Summarization and Consistency Check
        final_summary = await self.summarize(
            instruction="""Create concise summary of:
            1. Problem classification
            2. Solution approach
            3. Key edge cases handled
            4. Validation results
            Ensure summary logically aligns with original problem and final solution.""",
            context=f"Classification: {classification}\nFinal Solution: {best_solution}"
        )

        # Return final solution (extract code if wrapped in markdown)
        if "