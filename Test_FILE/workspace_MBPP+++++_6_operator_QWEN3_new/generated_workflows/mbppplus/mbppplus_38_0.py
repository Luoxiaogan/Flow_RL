# Workflow ID: mbppplus_38_0
# Benchmark: mbppplus
# Data Indices: [24, 195]

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
        
        # Phase 1: Problem Decomposition - Identify core requirements and edge cases
        decomposition = await self.decompose(
            instruction="""Break this programming problem into atomic subproblems. For each:
            1. Identify the core transformation or computation required
            2. List all edge cases (empty inputs, single elements, duplicates, type boundaries)
            3. Specify exact input/output types and constraints
            4. Note any implicit requirements from test cases
            Return as structured list with clear, actionable subproblems.""",
            context=""
        )
        
        # Phase 2: Parallel Solution Generation - Create diverse solution approaches
        solution_approaches = [
            "mathematical_precise",
            "defensive_robust",
            "functional_style", 
            "imperative_step_by_step"
        ]
        
        solution_tasks = []
        for approach in solution_approaches:
            task = self.generate(
                instruction=f"""Generate a complete Python solution using {approach} approach:
                - Handle ALL edge cases identified in decomposition
                - Match exact return type and structure
                - Include type hints and clear variable names
                - Add inline comments explaining key logic
                - Prioritize correctness over performance
                Base your solution on this decomposition: {json.dumps(decomposition)}""",
                context=""
            )
            solution_tasks.append(task)
        
        candidate_solutions = await asyncio.gather(*solution_tasks)
        
        # Phase 3: Ensemble Synthesis - Combine best elements from all candidates
        synthesized_solution = await self.ensemble(
            instruction="""Create the optimal solution by synthesizing the best aspects of all candidates:
            - Take correct edge-case handling from whichever solution does it best
            - Adopt the clearest logic structure
            - Ensure type consistency and return format matches requirements
            - Remove redundant code while preserving robustness
            - Add comprehensive comments explaining how edge cases are handled
            Output ONLY the final Python function with imports if needed.""",
            contexts_list=candidate_solutions
        )
        
        # Phase 4: Iterative Validation & Refinement Loop
        current_solution = synthesized_solution
        for iteration in range(3):  # Max 3 refinement cycles
            # Programmer self-tests with edge cases
            execution_result = await self.programmer(
                instruction=f"""Execute this solution against comprehensive test cases including:
                - Empty inputs
                - Single element cases  
                - Boundary values
                - Duplicate elements
                - Type edge cases
                If any test fails, revise the code to fix it. Return the corrected code.
                Current solution: {current_solution}""",
                context=current_solution,
                max_retries=1
            )
            
            # Meta-validation: Analyze solution for hidden flaws
            validation_report = await self.generate(
                instruction=f"""Critically analyze this solution:
                1. Does it handle ALL edge cases from decomposition?
                2. Is return type exactly as required?
                3. Are there any type assumptions that could break?
                4. Could it fail on any implicit test cases?
                5. Is logic clear and maintainable?
                Return structured report with 'issues' list and 'suggested_fixes'.""",
                context=execution_result
            )
            
            # Check if validation found critical issues
            if "no issues" in validation_report.lower() or "all good" in validation_report.lower():
                break
                
            # Revise based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation report:
                Validation: {validation_report}
                Current solution: {execution_result}
                Make minimal changes needed to address issues while preserving working functionality.""",
                context=execution_result
            )
        else:
            # Fallback: If still failing after 3 iterations, use conservative approach
            current_solution = await self.generate(
                instruction=f"""Generate a maximally defensive solution:
                - Handle every possible edge case explicitly
                - Add type checking and assertions
                - Follow examples' structure exactly
                - Prioritize robustness over elegance
                Based on original problem and decomposition: {json.dumps(decomposition)}""",
                context=""
            )
        
        # Final polish: Ensure clean, production-ready code
        final_solution = await self.revise(
            instruction="""Final polish:
            - Remove any debug prints or unnecessary comments
            - Ensure PEP8 compliance
            - Verify function signature matches exactly
            - Include only necessary imports
            - Return ONLY the function implementation as required""",
            context=current_solution
        )
        
        return final_solution