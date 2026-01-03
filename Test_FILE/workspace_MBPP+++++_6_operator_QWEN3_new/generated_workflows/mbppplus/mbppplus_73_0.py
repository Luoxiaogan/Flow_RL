# Workflow ID: mbppplus_73_0
# Benchmark: mbppplus
# Data Indices: [273, 136]

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

        # PHASE 1: Decompose the problem into core logical conditions and edge cases
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental logical conditions and edge cases.
            Focus exclusively on WHAT must be true for a solution to be correct, not HOW to implement it.
            Identify:
            - Core validation rules (e.g., 'string length must be divisible', 'must start with vowel')
            - Critical edge cases (empty inputs, single elements, boundary values)
            - Expected input/output types and constraints
            - Any implicit assumptions that must be handled
            Format each condition as a clear, testable statement.""",
            context=""
        )
        
        # Convert decomposition to readable format for subsequent steps
        decomposition_text = "\n".join([f"{item['id']}: {item['description']}" for item in decomposition])

        # PHASE 2: Generate multiple solution variants in parallel
        solution_variants = await asyncio.gather(
            self.programmer(
                instruction=f"""Generate a Python function that solves the problem by directly implementing these logical conditions:
                {decomposition_text}
                
                Requirements:
                - Match the exact function signature from the problem
                - Handle all edge cases identified above
                - Return the correct data type (bool, string, etc.)
                - Use efficient, clean code with no external libraries unless necessary
                - Include no comments or explanations — only the function implementation
                - Test mentally against edge cases before finalizing""",
                context="",
                max_retries=2
            ),
            self.programmer(
                instruction=f"""Generate a Python function using an alternative algorithmic approach while satisfying:
                {decomposition_text}
                
                Requirements:
                - Use a different strategy than the most obvious solution (e.g., if obvious is iterative, try recursive or functional)
                - Still handle all edge cases and match function signature
                - Prioritize clarity and correctness over cleverness
                - Return only the function implementation, no extra text""",
                context="",
                max_retries=2
            ),
            self.programmer(
                instruction=f"""Generate a Python function that solves the problem with defensive programming and explicit edge case handling:
                {decomposition_text}
                
                Requirements:
                - Include explicit checks for each edge case identified
                - Use guard clauses and early returns where appropriate
                - Match function signature exactly
                - Return only the function implementation""",
                context="",
                max_retries=2
            )
        )

        # PHASE 3: Ensemble-based validation and selection
        selected_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below. Evaluate based on:
            1. Correctness: Does it handle all logical conditions and edge cases from the decomposition?
            2. Robustness: Does it gracefully handle unexpected inputs?
            3. Simplicity: Is the code clear and maintainable?
            4. Efficiency: Is it reasonably efficient for the problem constraints?
            
            Mentally simulate each solution against these test cases (even if not provided in original problem):
            - Empty inputs
            - Single element inputs
            - Boundary values
            - Invalid or edge-case inputs
            
            If all solutions have flaws, identify the most fixable one and note the specific issues.
            Return ONLY the selected function implementation — no explanations or markdown.""",
            contexts_list=solution_variants
        )

        # PHASE 4: Optional refinement loop (if ensemble indicates uncertainty or flaws)
        refinement_instruction = await self.generate(
            instruction="""Analyze the selected solution and determine if it needs refinement.
            Look for:
            - Any edge cases from decomposition that might still be unhandled
            - Potential off-by-one errors or type mismatches
            - Logical gaps or inefficiencies
            If no issues found, return 'APPROVED'.
            If issues found, return a specific revision instruction detailing exactly what to fix.""",
            context=selected_solution
        )

        final_solution = selected_solution
        if "APPROVED" not in refinement_instruction.upper():
            # Attempt one refinement
            final_solution = await self.revise(
                instruction=f"""Revise this code to fix the specific issues identified:
                {refinement_instruction}
                
                Also ensure:
                - All decomposition conditions are still satisfied
                - Function signature is unchanged
                - Code remains clean and efficient
                Return ONLY the revised function implementation.""",
                context=selected_solution
            )

        return final_solution