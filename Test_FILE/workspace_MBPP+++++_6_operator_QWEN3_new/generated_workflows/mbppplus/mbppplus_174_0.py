# Workflow ID: mbppplus_174_0
# Benchmark: mbppplus
# Data Indices: [327, 113]

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
        import json
        
        # Phase 1: Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental computational subproblems.
            Identify:
            1. Input/output data types and formats
            2. Core algorithmic operations needed
            3. Edge cases and boundary conditions
            4. Potential solution strategies
            5. Dependencies between subproblems
            Return structured subproblems with clear descriptions and dependencies.""",
            context=""
        )
        
        # Phase 2: Parallel Solution Generation
        # Generate multiple solution approaches simultaneously
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the problem decomposition: {json.dumps(decomposition)}
                Generate a solution using direct string manipulation and parsing.
                Focus on: clear variable names, handling edge cases, and matching exact output format.
                Include all necessary imports and use the exact function signature specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem decomposition: {json.dumps(decomposition)}
                Generate a solution using regular expressions or pattern matching.
                Focus on: robust pattern handling, edge case coverage, and efficiency.
                Include all necessary imports and use the exact function signature specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem decomposition: {json.dumps(decomposition)}
                Generate a solution using mathematical or algorithmic approaches.
                Focus on: computational efficiency, correctness for all inputs, and clean logic.
                Include all necessary imports and use the exact function signature specified.""",
                context=""
            )
        )
        
        # Phase 3: Solution Synthesis
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all provided solutions into a single robust implementation.
            Prioritize:
            1. Correctness for all edge cases (empty inputs, boundary values, etc.)
            2. Exact match to required function signature and return types
            3. Clean, readable code with appropriate variable names
            4. Computational efficiency
            5. Proper error handling and defensive programming
            Return ONLY the final function implementation with necessary imports, nothing else.""",
            contexts_list=solution_approaches
        )
        
        # Phase 4: Code Validation and Refinement
        # Try to execute against visible test cases if available
        try:
            validated_code = await self.programmer(
                instruction=f"""Validate and refine this code against the problem requirements:
                {synthesized_solution}
                
                Ensure:
                1. Code executes without errors
                2. Passes all visible test cases
                3. Handles edge cases not explicitly mentioned
                4. Uses correct data types (list vs tuple vs set)
                5. Follows exact function signature
                6. Includes all necessary imports at top
                Return ONLY the final implementation, nothing else.""",
                context=synthesized_solution,
                max_retries=3
            )
        except Exception:
            # If validation fails, fall back to synthesized solution
            validated_code = synthesized_solution
        
        # Phase 5: Final Robustness Check
        final_code = await self.revise(
            instruction="""Perform final robustness check on this code:
            1. Verify function signature matches exactly what's required
            2. Ensure all imports are included and at top
            3. Check for edge case handling (empty inputs, single elements, duplicates, etc.)
            4. Confirm return type matches requirements
            5. Remove any extraneous text, comments, or wrapper code
            6. Ensure code is production-ready with no debugging statements
            Return ONLY the clean function implementation with necessary imports, nothing else.""",
            context=validated_code
        )
        
        return final_code