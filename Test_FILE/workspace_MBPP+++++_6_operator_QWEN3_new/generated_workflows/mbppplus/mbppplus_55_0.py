# Workflow ID: mbppplus_55_0
# Benchmark: mbppplus
# Data Indices: [149, 38]

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

        # Step 1: Decompose the problem into structured components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into essential components:
            1. INPUT SPECIFICATION: What are the input parameters? What types are expected? Any constraints?
            2. TRANSFORMATION LOGIC: What operations need to be performed? Step by step.
            3. OUTPUT SPECIFICATION: What should be returned? Exact type and format.
            4. EDGE CASES: What edge cases must be handled? (empty inputs, single elements, type boundaries, etc.)
            5. SPECIAL REQUIREMENTS: Order preservation? Type conversion? Error handling?
            Return as structured list of subproblems with clear dependencies.""",
            context=""
        )

        # Step 2: Generate problem classification to determine solution strategy
        classification = await self.generate(
            instruction=f"""Based on this decomposition:
            {decomposition}
            
            Classify this problem for optimal solution strategy:
            - CATEGORY: Is this a direct transformation, filter-reduce, mathematical computation, set operation, or logic validation?
            - COMPLEXITY: Simple (single operation) or Complex (multi-step with conditions)?
            - TYPE_SENSITIVITY: Does return type matter critically? (list vs tuple vs set vs scalar)
            - EDGE_CASE_CRITICAL: Are edge cases likely to cause failures?
            - STRATEGY: Recommend 2-3 different solution approaches with pros/cons.
            Provide structured classification with clear labels.""",
            context=str(decomposition)
        )

        # Step 3: Parallel generation of multiple solution candidates using different strategies
        strategy_instructions = [
            """Generate a direct, minimal implementation focusing on core logic. 
            Assume standard edge cases are handled. Prioritize simplicity and readability.
            Include type hints in code comments. Return only the function implementation.""",
            
            """Generate a defensive, comprehensive implementation.
            Explicitly handle all edge cases mentioned in decomposition.
            Add inline comments for each edge case check.
            Ensure type consistency and include assertions if appropriate.
            Return only the function implementation.""",
            
            """Generate a step-by-step implementation with intermediate variables.
            Break down complex operations into clear, named steps.
            Include detailed comments explaining each transformation.
            Prioritize maintainability and clarity over brevity.
            Return only the function implementation."""
        ]

        # Generate solutions in parallel
        solution_candidates = await asyncio.gather(
            *[self.programmer(
                instruction=f"""{strategy_instructions[i]}
                
                Problem Context:
                {classification}
                
                Decomposition:
                {decomposition}
                
                Generate Python code that solves the problem exactly as specified.
                Remember: Return ONLY the function implementation with necessary imports.
                Match the exact function signature from the problem.
                Handle edge cases and type requirements as specified.""",
                context=f"{classification}\n\n{decomposition}"
            ) for i in range(len(strategy_instructions))]
        )

        # Step 4: Ensemble - select best solution based on decomposition contract
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            1. CORRECTNESS: Must match decomposition requirements exactly
            2. EDGE CASE HANDLING: Must address all edge cases identified
            3. TYPE SAFETY: Must return correct type as specified
            4. READABILITY: Clear, maintainable code
            5. EFFICIENCY: Reasonable performance for problem scale
            
            Decomposition for reference:
            {decomposition}
            
            Return ONLY the selected code implementation. No explanations.""",
            contexts_list=solution_candidates
        )

        # Step 5: Validate and iteratively refine if needed
        for iteration in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {best_solution}
                
                Against original decomposition:
                {decomposition}
                
                Check:
                1. Does it handle ALL edge cases specified?
                2. Does it return the EXACT required type?
                3. Does it match the function signature?
                4. Are there any logical errors or oversights?
                5. Is the code robust against unexpected inputs?
                
                If perfect, respond with 'VALIDATED'.
                If issues found, describe them concisely and specifically.""",
                context=best_solution
            )

            if "VALIDATED" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break  # Exit loop if validated
            
            # Revise based on validation feedback
            best_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                {validation}
                
                While preserving:
                - Correct function signature
                - Required return type
                - Core logic correctness
                - Readability and maintainability
                
                Return ONLY the revised code implementation.""",
                context=best_solution
            )

        return best_solution