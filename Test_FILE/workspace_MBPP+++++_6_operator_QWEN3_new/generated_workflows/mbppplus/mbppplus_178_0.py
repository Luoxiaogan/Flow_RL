# Workflow ID: mbppplus_178_0
# Benchmark: mbppplus
# Data Indices: [264, 296]

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

        # Step 1: Deep problem analysis and classification
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem:
            1. Identify the core operation: Is it transformation, filtering, searching, validation, or computation?
            2. Determine input/output types: What data structures are involved (list, tuple, string, etc.)?
            3. Extract key constraints: Order preservation? Uniqueness? Case sensitivity? Mutability?
            4. Enumerate edge cases: Empty inputs, single elements, duplicates, type boundaries, special values.
            5. Suggest solution strategies: Functional (map/filter), iterative, mathematical, set operations, etc.
            6. Note any hidden requirements from examples (e.g., exact matching vs substring).
            Format as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Generate edge case test scenarios
        edge_cases = await self.generate(
            instruction=f"""Based on this analysis:
            {analysis}
            
            Generate 5-7 comprehensive test cases including:
            - Typical cases (from examples)
            - Edge cases (empty, single element, duplicates, boundaries)
            - Error cases (invalid types, None values)
            Format as Python assert statements.""",
            context=analysis
        )

        # Step 3: Parallel solution generation with different strategies
        solution_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Generate a clean, efficient solution focusing on readability and clarity.
                Problem Analysis: {analysis}
                Key Requirements: Match function signature exactly, handle all edge cases, return correct type.
                Prefer functional programming style (map, filter) if applicable.""",
                context=analysis
            ),
            self.programmer(
                instruction=f"""Generate a robust, defensive solution with explicit edge case handling.
                Problem Analysis: {analysis}
                Key Requirements: Include input validation, comprehensive error handling, verbose comments.
                Use explicit loops and conditionals for maximum clarity.""",
                context=analysis
            ),
            self.programmer(
                instruction=f"""Generate a performance-optimized solution minimizing operations.
                Problem Analysis: {analysis}
                Key Requirements: Use built-in functions and comprehensions, avoid unnecessary variables.
                Prioritize speed and memory efficiency.""",
                context=analysis
            )
        )

        # Step 4: Ensemble selection based on correctness and quality
        selected_solution = await self.ensemble(
            instruction=f"""Evaluate these candidate solutions against the problem requirements and test cases:
            Test Cases: {edge_cases}
            Analysis: {analysis}
            
            Selection Criteria:
            1. Correctness: Must handle all test cases including edge cases
            2. Type Compliance: Return type must match exactly (list/tuple/set)
            3. Code Quality: Clean, readable, follows Python best practices
            4. Efficiency: Reasonable time/space complexity
            5. Robustness: Graceful handling of unexpected inputs
            
            Return the best solution. If none are perfect, synthesize a hybrid solution combining strengths.""",
            contexts_list=solution_attempts
        )

        # Step 5: Targeted revision for compliance and edge cases
        final_solution = await self.revise(
            instruction=f"""Revise this solution to ensure perfect compliance:
            1. Function name must match EXACTLY as specified
            2. Include all necessary imports at top
            3. Handle ALL edge cases from analysis: {analysis}
            4. Return correct data type (list/tuple/set) as shown in examples
            5. No wrapper functions or classes - only the implementation
            6. Add minimal comments only if they clarify non-obvious logic
            
            Final output must be ready for automated testing with hundreds of cases.""",
            context=selected_solution
        )

        # Step 6: Validation and fallback decomposition if needed
        validation = await self.generate(
            instruction=f"""Validate this final solution:
            Solution: {final_solution}
            Analysis: {analysis}
            Edge Cases: {edge_cases}
            
            Check for:
            - Syntax errors
            - Missing imports
            - Incorrect function signature
            - Unhandled edge cases
            - Type mismatches
            
            If any issues found, describe them precisely. Otherwise, return 'VALID'.""",
            context=final_solution
        )

        if "VALID" not in validation.upper():
            # Fallback: Decompose and solve step by step
            decomposition = await self.decompose(
                instruction="""Break this problem into atomic subproblems with clear dependencies.
                Each subproblem should be independently solvable and testable.
                Format as list of dictionaries with 'id', 'description', and 'dependencies'.""",
                context=f"Problem: {self.problem_text}
                Issues: {validation}"
            )
            
            # Solve each subproblem
            sub_solutions = {}
            for subproblem in decomposition:
                sub_id = subproblem['id']
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                dep_context = "
".join([sub_solutions.get(dep.strip(), "") for dep in deps if dep.strip() in sub_solutions])
                
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context from dependencies: {dep_context}
                    Overall problem: {self.problem_text}
                    Ensure output format matches parent requirements.""",
                    context=dep_context
                )
                sub_solutions[sub_id] = sub_solution
            
            # Synthesize final solution from subproblems
            synthesis_context = "
".join([f"Subproblem {k}: {v}" for k, v in sub_solutions.items()])
            final_solution = await self.generate(
                instruction=f"""Synthesize a complete solution from these subproblem solutions:
                {synthesis_context}
                
                Ensure:
                - Correct function signature
                - Proper integration of subproblem solutions
                - Handle all edge cases
                - Return correct data type
                - Clean, production-ready code""",
                context=synthesis_context
            )

        return final_solution