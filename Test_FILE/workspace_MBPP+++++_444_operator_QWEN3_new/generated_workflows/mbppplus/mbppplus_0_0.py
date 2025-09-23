# Workflow ID: mbppplus_0_0
# Benchmark: mbppplus
# Data Indices: [31, 339, 2]

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
        import re

        # Phase 1: Generate multiple problem interpretations
        interpretation_instructions = [
            """Analyze the problem from an algorithmic efficiency perspective:
            - Identify the core operation (sorting, filtering, generating, etc.)
            - Determine time/space complexity constraints
            - Note any in-place requirements
            - Highlight key edge cases (empty, single element, duplicates)
            - Suggest optimal data structures and algorithms""",
            
            """Analyze the problem from a robustness and edge-case perspective:
            - List all possible boundary conditions
            - Consider type variations (lists, tuples, sets)
            - Identify potential overflow or underflow scenarios
            - Note any mathematical constraints or invariants
            - Suggest defensive programming approaches""",
            
            """Analyze the problem from a readability and maintainability perspective:
            - Suggest clear variable names and structure
            - Identify opportunities for helper functions
            - Note any complex logic that needs clear comments
            - Suggest error handling for invalid inputs
            - Emphasize code clarity over cleverness"""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in interpretation_instructions]
        )

        # Phase 2: Generate candidate solutions based on each interpretation
        solution_instructions = [
            f"""Generate a complete Python function implementation based on this interpretation:
            {interp}
            
            Requirements:
            - Use EXACT function name and signature from problem
            - Include all necessary imports inside function if needed
            - Handle ALL edge cases mentioned in interpretation
            - Return correct data type (list, tuple, set, etc.)
            - Code must be self-contained and runnable
            - Follow Python best practices
            
            Format: ONLY the function implementation, nothing else.""",
            f"""Generate a complete Python function implementation based on this interpretation:
            {interp}
            
            Requirements:
            - Use EXACT function name and signature from problem
            - Include all necessary imports inside function if needed
            - Handle ALL edge cases mentioned in interpretation
            - Return correct data type (list, tuple, set, etc.)
            - Code must be self-contained and runnable
            - Follow Python best practices
            
            Format: ONLY the function implementation, nothing else.""",
            f"""Generate a complete Python function implementation based on this interpretation:
            {interp}
            
            Requirements:
            - Use EXACT function name and signature from problem
            - Include all necessary imports inside function if needed
            - Handle ALL edge cases mentioned in interpretation
            - Return correct data type (list, tuple, set, etc.)
            - Code must be self-contained and runnable
            - Follow Python best practices
            
            Format: ONLY the function implementation, nothing else."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in solution_instructions]
        )

        # Phase 3: Ensemble - synthesize best solution
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions:
            - Combine algorithmic efficiency with robustness and readability
            - Ensure all edge cases from all interpretations are handled
            - Choose the clearest, most maintainable implementation
            - Verify function signature matches exactly
            - Ensure output format is correct (list, tuple, set, etc.)
            - Remove any unnecessary complexity
            
            Output ONLY the final function implementation, nothing else.""",
            contexts_list=candidate_solutions
        )

        # Phase 4: Validation and refinement loop
        current_solution = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {current_solution}
                
                Tasks:
                1. Generate 5 edge cases not shown in examples (consider: empty inputs, single elements, extreme values, duplicates, type variations)
                2. For each edge case, explain why it's important and what the correct output should be
                3. Test the solution against these edge cases (simulate execution mentally)
                4. List any bugs, inefficiencies, or violations of requirements
                5. If no issues found, output "VALIDATED"
                
                Be brutally honest - any flaw must be reported.""",
                context=current_solution
            )

            if "VALIDATED" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Fix all issues identified in validation:
                    {validation}
                    
                    Requirements:
                    - Maintain exact function signature
                    - Handle ALL edge cases mentioned in validation
                    - Preserve algorithmic correctness
                    - Keep code clean and readable
                    - Output ONLY the function implementation, nothing else
                    
                    Issues to fix: {validation}""",
                    context=current_solution
                )

        # Final format enforcement
        final_solution = await self.revise(
            instruction="""Ensure this is PERFECTLY formatted:
            - ONLY the function implementation (no explanations, no markdown)
            - Correct function name and signature
            - All imports inside function if needed
            - No extra text before or after
            - Proper indentation and Python syntax
            - Return correct data type as specified
            
            If already perfect, return unchanged. Otherwise, fix formatting only.""",
            context=current_solution
        )

        return final_solution