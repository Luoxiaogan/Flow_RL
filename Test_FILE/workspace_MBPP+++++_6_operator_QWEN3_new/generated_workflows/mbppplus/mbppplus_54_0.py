# Workflow ID: mbppplus_54_0
# Benchmark: mbppplus
# Data Indices: [133, 8]

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

        # Step 1: Problem Classification & Complexity Triage
        classification = await self.generate(
            instruction="""Analyze this programming problem with extreme precision. Your analysis must include:
            1. Problem Type: Is this primarily mathematical, algorithmic, data transformation, or logical?
            2. Complexity Level: Simple (direct formula), Moderate (requires 1-2 loops), Complex (requires recursion, DP, or multiple steps)
            3. Key Operations: What core operations are needed? (e.g., summation, product, min/max, string parsing)
            4. Edge Case Categories: What types of edge cases must be handled? (empty inputs, single elements, zeros, negatives, boundaries)
            5. Expected Solution Pattern: Does this resemble known patterns? (sliding window, greedy, DP, mathematical identity)
            6. Input/Output Specification: What are the exact input parameters and expected return type?
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Step 2: Parallel Edge Case & Solution Strategy Generation
        edge_case_analysis, solution_strategy = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the classification:
                {classification}
                
                Generate comprehensive edge case scenarios. For each, specify:
                - Input values
                - Expected behavior
                - Why this edge case matters
                Cover at minimum: empty inputs, single element, all zeros, negative values, maximum/minimum boundaries, duplicates.
                Format as numbered list with clear input/output expectations.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on the classification:
                {classification}
                
                Develop a detailed solution strategy. Include:
                - Step-by-step algorithm in plain English
                - Mathematical insights or formulas if applicable
                - Data structures to use
                - Time/space complexity analysis
                - Why this approach handles the identified edge cases
                - Alternative approaches considered and rejected
                Structure as: Strategy Overview, Detailed Steps, Complexity, Edge Case Handling, Alternatives.""",
                context=classification
            )
        )

        # Step 3: Conditional Decomposition (Only for Complex Problems)
        if "complex" in classification.lower() or "multiple steps" in classification.lower() or "recursion" in classification.lower():
            decomposition = await self.decompose(
                instruction=f"""Break down this complex problem into minimal, independent subproblems:
                - Each subproblem should be solvable in isolation
                - Specify dependencies between subproblems
                - Focus on computational steps, not conceptual breakdown
                - Aim for 2-5 subproblems maximum
                Use the solution strategy as guide:
                {solution_strategy}""",
                context=solution_strategy
            )
            
            # Solve subproblems in parallel where possible
            subproblem_solutions = []
            for subproblem in decomposition:
                if not subproblem.get('dependencies'):
                    solution = await self.programmer(
                        instruction=f"""Implement this subproblem:
                        {subproblem['description']}
                        
                        Requirements:
                        - Return only the computational result or function snippet
                        - Handle edge cases specified in overall analysis
                        - Use efficient approach
                        - No print statements or explanations""",
                        context=edge_case_analysis
                    )
                    subproblem_solutions.append(solution)
            
            # Synthesize subproblem solutions
            synthesized_solution = await self.generate(
                instruction=f"""Combine these subproblem solutions into a complete answer:
                Subproblems: {decomposition}
                Solutions: {subproblem_solutions}
                Edge Cases: {edge_case_analysis}
                
                Generate final implementation that:
                - Integrates all subproblem solutions
                - Maintains correct function signature
                - Handles all edge cases
                - Is production-ready and efficient""",
                context=f"{solution_strategy}\n\n{subproblem_solutions}"
            )
            implementation_context = synthesized_solution
        else:
            # Direct implementation for simple/moderate problems
            implementation_context = solution_strategy

        # Step 4: Generate Initial Code Implementation
        initial_implementation = await self.programmer(
            instruction=f"""Generate Python code that solves the problem exactly as specified.
            CRITICAL REQUIREMENTS:
            - Use EXACT function name and parameters from problem
            - Return correct data type (int, list, tuple, etc.)
            - Handle ALL edge cases identified earlier
            - Include no imports unless absolutely necessary
            - Code must be self-contained and runnable
            - No explanatory comments or print statements
            - Optimize for correctness, not brevity
            
            Reference these analyses:
            Solution Strategy: {solution_strategy}
            Edge Cases: {edge_case_analysis}
            
            OUTPUT ONLY THE FUNCTION IMPLEMENTATION. NOTHING ELSE.""",
            context=implementation_context
        )

        # Step 5: Self-Critique and Revision Loop (max 2 iterations)
        current_implementation = initial_implementation
        for iteration in range(2):
            critique = await self.generate(
                instruction=f"""Critically review this implementation:
                {current_implementation}
                
                Check for:
                1. Correctness: Does it match the problem requirements?
                2. Edge Case Handling: Does it handle all identified edge cases?
                3. Efficiency: Is the approach optimal?
                4. Code Quality: Is it clean, readable, and follows Python conventions?
                5. Signature Compliance: Does it use the exact function name and parameters?
                6. Return Type: Does it return the expected data type?
                
                If any issues found, provide specific, actionable revision instructions.
                If perfect, respond with 'APPROVED'.""",
                context=f"{edge_case_analysis}\n\n{solution_strategy}"
            )
            
            if "APPROVED" in critique.upper():
                break
                
            revised_implementation = await self.revise(
                instruction=f"""Revise the implementation based on this critique:
                {critique}
                
                Requirements:
                - Fix all identified issues
                - Maintain all previously handled edge cases
                - Keep function signature identical
                - Return only the revised function implementation
                - No additional text or explanations""",
                context=current_implementation
            )
            current_implementation = revised_implementation

        # Step 6: Final Validation Ensemble
        validation_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Validate implementation against original problem:
                Implementation: {current_implementation}
                Problem: {self.problem_text}
                
                Does this solve the problem exactly as specified? Check function signature, return type, and logic.
                Respond with 'VALID' or 'INVALID' followed by brief reason.""",
                context=current_implementation
            ),
            self.generate(
                instruction=f"""Validate implementation against edge cases:
                Implementation: {current_implementation}
                Edge Cases: {edge_case_analysis}
                
                Does this handle all edge cases correctly? Test each one mentally.
                Respond with 'EDGE_VALID' or 'EDGE_INVALID' followed by which cases fail.""",
                context=current_implementation
            )
        )

        final_validation = await self.ensemble(
            instruction="""Make final determination:
            - If both validations pass, return the implementation unchanged
            - If either fails, return a fallback implementation that at minimum handles basic cases
            - Prioritize correctness over elegance
            - Must return valid Python function code""",
            contexts_list=[current_implementation] + validation_approaches
        )

        return final_validation