# Workflow ID: mbppplus_46_0
# Benchmark: mbppplus
# Data Indices: [213, 313]

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

        # Step 1: Meta-Analysis - Classify problem type and strategy
        problem_analysis = await self.generate(
            instruction="""Perform deep meta-analysis of this programming problem:
            1. Classify problem category: mathematical, string manipulation, logical validation, data structure, or hybrid.
            2. Identify input/output types and constraints (e.g., string, list, int, edge cases like empty inputs).
            3. Determine if solution requires formula, algorithm, pattern matching, or multi-step decomposition.
            4. Suggest optimal solution strategy: direct computation, iterative logic, recursive approach, or combinatorial analysis.
            5. Predict potential edge cases and failure modes.
            6. Recommend whether decomposition is necessary or if direct code generation suffices.
            Format response as structured JSON with keys: category, input_type, output_type, strategy, needs_decomposition, edge_cases.""",
            context=""
        )

        # Step 2: Dynamic routing based on analysis
        try:
            analysis_json = json.loads(problem_analysis)
            needs_decomp = analysis_json.get("needs_decomposition", False)
            category = analysis_json.get("category", "")
        except:
            # Fallback: assume complex if parsing fails
            needs_decomp = True
            category = "unknown"

        # Step 3: Parallel strategy generation - create multiple solution approaches
        strategy_context = f"Problem Analysis: {problem_analysis}"
        
        if needs_decomp:
            # Generate decomposition and parallel solution attempts
            decomposition = await self.decompose(
                instruction=f"""Break this problem into minimal, independent subproblems:
                - Each subproblem should be solvable in isolation
                - Specify dependencies between subproblems
                - Focus on separating concerns (e.g., parsing, validation, computation)
                - Include edge case handling as explicit subproblems""",
                context=strategy_context
            )
            
            # Generate solutions for each subproblem in parallel
            subproblem_solutions = []
            for subproblem in decomposition:
                solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context: {strategy_context}
                    Requirements:
                    - Handle all edge cases mentioned in analysis
                    - Return correct data type
                    - Be self-contained and testable
                    - Include comments explaining logic""",
                    context=subproblem['description']
                )
                subproblem_solutions.append(solution)
            
            # Synthesize subproblem solutions into complete solution
            complete_solution = await self.ensemble(
                instruction="""Synthesize these subproblem solutions into a complete, coherent solution:
                - Ensure proper integration between subproblems
                - Maintain consistent variable naming and style
                - Add necessary glue code and error handling
                - Verify that edge cases from all subproblems are addressed
                - Format as a single Python function with proper signature""",
                contexts_list=subproblem_solutions
            )
        else:
            # Direct code generation for simple problems
            code_attempts = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate Python code for this problem:
                    - Follow exact function signature
                    - Handle all edge cases identified in analysis
                    - Return correct data type
                    - Include minimal necessary comments
                    - Prioritize correctness over optimization""",
                    context=strategy_context
                ),
                self.generate(
                    instruction=f"""Generate algorithmic pseudocode solution:
                    - Step-by-step logical breakdown
                    - Include edge case handling
                    - Specify input validation steps
                    - Describe return value construction""",
                    context=strategy_context
                )
            )
            
            # Ensemble code and pseudocode into final solution
            complete_solution = await self.ensemble(
                instruction="""Combine the generated code and pseudocode into the optimal solution:
                - Use code as base but incorporate pseudocode's edge case handling
                - Ensure type consistency and proper function signature
                - Add comments for complex logic
                - Verify against problem requirements""",
                contexts_list=code_attempts
            )

        # Step 4: Validation and refinement loop
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                - Check for all edge cases mentioned in initial analysis
                - Verify type consistency (input/output)
                - Test logical completeness (no missing conditions)
                - Ensure function signature matches exactly
                - Identify any potential bugs or oversights
                - Suggest specific improvements
                Return 'VALID' if perfect, otherwise detailed critique.""",
                context=complete_solution
            )
            
            if "VALID" in validation.upper() and len(validation) < 20:
                break  # Solution is validated
            
            # Revise based on validation feedback
            complete_solution = await self.revise(
                instruction=f"""Improve this solution based on validation feedback:
                Validation Feedback: {validation}
                
                Requirements:
                - Fix all identified issues
                - Maintain function signature
                - Preserve working functionality
                - Add missing edge case handling
                - Improve clarity with comments if needed""",
                context=complete_solution
            )

        # Step 5: Final verification and cleanup
        final_solution = await self.revise(
            instruction="""Final polish:
            - Ensure code is clean, readable, and follows Python best practices
            - Verify function signature is exactly as required
            - Confirm all edge cases are handled
            - Remove any debug statements or unnecessary comments
            - Return ONLY the function implementation with imports if needed""",
            context=complete_solution
        )

        return final_solution