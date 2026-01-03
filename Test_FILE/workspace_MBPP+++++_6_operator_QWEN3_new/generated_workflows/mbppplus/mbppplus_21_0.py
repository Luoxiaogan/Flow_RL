# Workflow ID: mbppplus_21_0
# Benchmark: mbppplus
# Data Indices: [358, 354]

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

        # Step 1: Meta-analysis - Classify problem type and constraints
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis. Classify the problem by:
            1. Primary domain: numerical, logical, string, data structure, or algorithmic
            2. Key operations needed: arithmetic, iteration, recursion, set operations, etc.
            3. Edge cases to consider: empty inputs, single elements, zeros, negatives, duplicates
            4. Return type requirements: must match exactly (list vs tuple vs set vs scalar)
            5. Performance constraints: time/space complexity if implied
            6. Special conditions: order preservation, mutability, side effects
            Provide structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Parallel solution generation - 3 different approaches
        direct_solution, defensive_solution, decomposed_path = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, concise solution based on problem analysis:
                {problem_analysis}
                Focus on correctness and simplicity. Assume standard edge cases unless specified otherwise.
                Output ONLY the function implementation with necessary imports inside the function.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a defensive, robust solution that explicitly handles all edge cases:
                {problem_analysis}
                Include input validation, type checking, and graceful error handling.
                Output ONLY the function implementation with necessary imports inside the function.""",
                context=""
            ),
            self.decompose(
                instruction=f"""Decompose this problem into subproblems based on analysis:
                {problem_analysis}
                Break down into logical steps with clear dependencies. Focus on separable components.
                Return structured subproblem list.""",
                context=""
            )
        )

        # Step 3: Generate solution from decomposition (if decomposition was successful)
        decomposed_solution = ""
        try:
            if isinstance(decomposed_path, list) and len(decomposed_path) > 0:
                # Convert decomposition to string for context
                decomposition_str = "\n".join([
                    f"Step {i+1} ({item.get('id', '')}): {item.get('description', '')} "
                    f"[Depends on: {item.get('dependencies', 'none')}]"
                    for i, item in enumerate(decomposed_path)
                ])
                
                decomposed_solution = await self.generate(
                    instruction=f"""Generate solution by implementing each subproblem step-by-step:
                    Decomposition:
                    {decomposition_str}
                    
                    Problem Analysis:
                    {problem_analysis}
                    
                    Implement each step in order, respecting dependencies. Output ONLY the final function implementation
                    with necessary imports inside the function.""",
                    context=""
                )
        except Exception:
            # Fallback if decomposition fails
            decomposed_solution = await self.generate(
                instruction=f"""Generate alternative solution since decomposition failed:
                {problem_analysis}
                Output ONLY the function implementation with necessary imports inside the function.""",
                context=""
            )

        # Step 4: Ensemble - Select or synthesize best solution
        solution_candidates = [direct_solution, defensive_solution, decomposed_solution]
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Must handle all edge cases identified in analysis
            2. Simplicity: Prefer concise, readable code unless complexity is necessary
            3. Robustness: Should handle unexpected inputs gracefully
            4. Type consistency: Return type must match problem requirements exactly
            5. Efficiency: Reasonable time/space complexity for problem domain
            If multiple solutions are good, synthesize the best elements into one final solution.
            Output ONLY the final Python function implementation with necessary imports inside the function.""",
            contexts_list=solution_candidates
        )

        # Step 5: Validation and refinement loop (up to 2 iterations)
        current_solution = selected_solution
        for iteration in range(2):
            validation_feedback = await self.revise(
                instruction=f"""Critically review this solution:
                {current_solution}
                
                Based on original problem and analysis:
                {problem_analysis}
                
                Check for:
                1. Edge case handling (empty inputs, boundaries, special values)
                2. Type consistency (return type matches requirements)
                3. Algorithmic correctness (logic matches problem intent)
                4. Code quality (readability, Pythonic practices)
                5. Potential bugs or oversights
                
                If issues found, provide specific revision instructions. If perfect, return 'APPROVED'.""",
                context=current_solution
            )
            
            if "APPROVED" in validation_feedback.upper():
                break
                
            # Revise based on feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution based on this feedback:
                {validation_feedback}
                
                Original problem analysis:
                {problem_analysis}
                
                Output ONLY the revised Python function implementation with necessary imports inside the function.""",
                context=current_solution
            )

        # Step 6: Final cleanup - Ensure exact format requirements
        final_output = await self.summarize(
            instruction="""Extract ONLY the Python function implementation from the text below.
            Ensure:
            1. Function signature matches exactly what's required
            2. All necessary imports are inside the function (if any)
            3. No extra text, explanations, or markdown
            4. Return type is correct
            5. Code is properly indented and syntactically valid
            
            If multiple functions are present, select the one that matches the problem's function signature.
            Output ONLY the raw Python code, nothing else.""",
            context=current_solution
        )

        return final_output