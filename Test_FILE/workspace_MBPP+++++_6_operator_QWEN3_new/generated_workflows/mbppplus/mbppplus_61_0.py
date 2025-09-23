# Workflow ID: mbppplus_61_0
# Benchmark: mbppplus
# Data Indices: [9, 135]

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
        import re

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental subproblems:
            1. Identify input data structures (lists, tuples, strings, etc.) and their properties
            2. Determine output requirements including data type and structure
            3. Extract the core transformation or algorithmic operation being requested
            4. Enumerate edge cases (empty inputs, single elements, boundary conditions)
            5. Identify any mathematical or logical constraints
            Return each as a separate subproblem with clear dependencies.""",
            context=""
        )

        # Step 2: Parallel analysis branches
        analysis_tasks = [
            self.generate(
                instruction="""Analyze the structural and type requirements:
                - What data types are involved in input and output?
                - Must order be preserved? Are duplicates allowed?
                - Are there mutability constraints?
                - What are the exact type signatures expected?
                Provide a detailed structural specification.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the algorithmic intent:
                - Is this a search, filter, transform, or reduce operation?
                - Does it involve indices, positions, or ordering?
                - Are there mathematical formulas or invariants?
                - What is the computational complexity expectation?
                Describe the core algorithmic pattern needed.""",
                context=""
            ),
            self.generate(
                instruction="""Enumerate edge cases and failure modes:
                - What happens with empty inputs?
                - What about single-element cases?
                - Are there boundary conditions (first/last element, out-of-bounds)?
                - Could there be type mismatches or invalid inputs?
                - What are the most likely bugs in naive implementations?
                List all edge cases that must be handled.""",
                context=""
            )
        ]
        
        structural_analysis, algorithmic_analysis, edge_case_analysis = await asyncio.gather(*analysis_tasks)

        # Step 3: Synthesize into unified specification
        specification = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, comprehensive problem specification:
            1. Combine structural requirements with algorithmic intent
            2. Integrate edge case handling into the core solution approach
            3. Create a precise function signature with type annotations
            4. Specify exact behavior for all edge cases
            5. Define success criteria for the implementation
            The output should be a complete, unambiguous specification that could be handed to a programmer.""",
            contexts_list=[structural_analysis, algorithmic_analysis, edge_case_analysis]
        )

        # Step 4: Generate initial code implementation
        code_attempt = await self.programmer(
            instruction=f"""Generate a Python function that satisfies this specification:
            {specification}
            
            Requirements:
            - Use the exact function name and parameters from the original problem
            - Handle all edge cases identified in the specification
            - Return the correct data type (list, tuple, set, etc.)
            - Include no unnecessary imports or wrapper code
            - Write defensive code that gracefully handles invalid inputs
            - Prioritize clarity and correctness over premature optimization""",
            context=specification,
            max_retries=1
        )

        # Step 5: Iterative adversarial refinement
        current_code = code_attempt
        for iteration in range(3):  # Maximum 3 refinement cycles
            critique = await self.generate(
                instruction=f"""Critique this code as a rigorous test engineer:
                {current_code}
                
                1. What edge cases might still break this implementation?
                2. Are there any type mismatches or boundary condition failures?
                3. Does it match the exact specification requirements?
                4. What inputs would cause incorrect behavior?
                5. How can the code be made more robust?
                Provide specific, actionable feedback for improvement.""",
                context=current_code
            )
            
            # Check if critique indicates no issues found
            if "no issues" in critique.lower() or "correct" in critique.lower() and "edge" not in critique.lower():
                break
                
            # Revise code based on critique
            current_code = await self.revise(
                instruction=f"""Improve this code based on the following critique:
                {critique}
                
                Requirements:
                - Fix all identified issues
                - Maintain the exact function signature
                - Preserve all previously handled edge cases
                - Do not introduce new bugs
                - Keep code clean and readable""",
                context=current_code
            )

        # Step 6: Final validation and cleanup
        final_code = await self.revise(
            instruction="""Final cleanup and validation:
            1. Ensure the code matches the original function signature exactly
            2. Remove any debug statements or unnecessary comments
            3. Verify type consistency throughout
            4. Confirm all edge cases are handled
            5. Format code according to PEP 8 guidelines
            Return only the clean, final implementation.""",
            context=current_code
        )

        return final_code