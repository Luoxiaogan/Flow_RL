# Workflow ID: mbppplus_98_0
# Benchmark: mbppplus
# Data Indices: [115, 257]

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

        # Step 1: Deep semantic analysis to understand requirements and edge cases
        semantic_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Extract:
            1. The exact input-output contract (types, formats, constraints)
            2. All explicit and implicit requirements
            3. Potential edge cases (empty inputs, single elements, boundaries, type variations)
            4. Whether the solution requires recursion, iteration, direct computation, or transformation
            5. Any hidden patterns or mathematical relationships implied
            6. Expected return type and format
            Present your analysis in structured bullet points with clear categorization.""",
            context=""
        )

        # Step 2: Classify problem complexity to determine strategy path
        classification = await self.generate(
            instruction=f"""Based on this semantic analysis:
            {semantic_analysis}
            
            Classify this problem using these dimensions:
            - Complexity Level: [trivial, moderate, complex]
            - Strategy Type: [direct_formula, iterative, recursive, transformation, conditional]
            - Data Structure: [flat, nested, mixed, string, numeric]
            - Edge Case Sensitivity: [low, medium, high]
            - Type Strictness: [lenient, strict]
            
            Output format: JSON-like dictionary with these keys. Be conservative in classification.""",
            context=semantic_analysis
        )

        # Step 3: Conditional branching based on classification
        if "trivial" in classification.lower() and ("direct_formula" in classification.lower() or "simple" in classification.lower()):
            # Direct path for simple problems
            solution_candidates = await asyncio.gather(
                self.generate(
                    instruction="""Generate the most straightforward, efficient solution.
                    Focus on minimalism and direct computation. Assume input validity.
                    Match function signature exactly. Return only the implementation code.""",
                    context=semantic_analysis
                ),
                self.generate(
                    instruction="""Generate a robust solution with edge case handling.
                    Include input validation and type checking. Prioritize correctness over brevity.
                    Match function signature exactly. Return only the implementation code.""",
                    context=semantic_analysis
                )
            )
        else:
            # Complex path requiring decomposition
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal necessary subproblems.
                Each subproblem should be independently solvable and have clear inputs/outputs.
                Prioritize logical separation over granularity. Include dependency relationships.
                Focus on computational steps, not implementation details.""",
                context=semantic_analysis
            )
            
            # Generate solution using decomposition as guide
            decomposition_summary = "\n".join([f"{d['id']}: {d['description']}" for d in decomposition])
            solution_candidates = await asyncio.gather(
                self.generate(
                    instruction=f"""Using this decomposition:
                    {decomposition_summary}
                    
                    Generate a clean, efficient solution. Use appropriate algorithmic patterns.
                    Handle edge cases mentioned in semantic analysis. Match function signature exactly.
                    Return only the implementation code.""",
                    context=semantic_analysis
                ),
                self.generate(
                    instruction=f"""Using this decomposition:
                    {decomposition_summary}
                    
                    Generate a highly robust solution with comprehensive error handling.
                    Include type checks, boundary validations, and fallback behaviors.
                    Match function signature exactly. Return only the implementation code.""",
                    context=semantic_analysis
                ),
                self.generate(
                    instruction=f"""Using this decomposition:
                    {decomposition_summary}
                    
                    Generate an optimized solution focusing on computational efficiency.
                    Use appropriate data structures and avoid unnecessary operations.
                    Match function signature exactly. Return only the implementation code.""",
                    context=semantic_analysis
                )
            )

        # Step 4: Ensemble best solution from candidates
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on these criteria:
            1. Correctness: Must handle all edge cases identified in semantic analysis
            2. Type Safety: Must preserve exact return type and format
            3. Efficiency: Should avoid unnecessary computation
            4. Readability: Should be clear and maintainable
            5. Completeness: Must match function signature exactly
            If multiple solutions satisfy criteria, prefer the most explicit over clever.
            Return only the selected implementation code, nothing else.""",
            contexts_list=solution_candidates
        )

        # Step 5: Validation and iterative refinement loop (max 2 iterations)
        current_solution = final_solution
        for iteration in range(2):
            validation_feedback = await self.programmer(
                instruction=f"""Critique this solution:
                {current_solution}
                
                Generate 3 test cases including edge cases (empty, boundary, invalid type).
                Simulate execution. Report:
                - Any type mismatches
                - Unhandled edge cases
                - Logic errors
                - Deviations from function signature
                - Efficiency concerns
                Provide specific line-by-line feedback for improvement.""",
                context=current_solution,
                max_retries=1
            )
            
            # Check if validation found critical issues
            if any(keyword in validation_feedback.lower() for keyword in ["error", "mismatch", "unhandled", "invalid", "fail"]):
                current_solution = await self.revise(
                    instruction=f"""Incorporate this validation feedback:
                    {validation_feedback}
                    
                    Revise the solution to fix all identified issues while preserving core logic.
                    Maintain exact function signature. Improve robustness without sacrificing efficiency.
                    Return only the revised implementation code.""",
                    context=current_solution
                )
            else:
                break  # No issues found, exit loop

        # Step 6: Final cleanup and return
        final_code = await self.revise(
            instruction="""Final cleanup pass:
            - Ensure code matches exact function signature from problem
            - Remove any debug statements or comments
            - Ensure proper indentation and Python conventions
            - Verify all edge cases from semantic analysis are handled
            - Return ONLY the clean implementation code, nothing else""",
            context=current_solution
        )

        return final_code