# Workflow ID: mbppplus_97_0
# Benchmark: mbppplus
# Data Indices: [58, 219]

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

        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Analyze the problem and classify it along these dimensions:
            1. Complexity Level: Trivial, Moderate, Complex
            2. Primary Category: Data Structure, Mathematical, Logical, String Manipulation, Algorithmic
            3. Input Type: List, Tuple, Set, String, Number, Mixed
            4. Output Type: List, Tuple, Set, Boolean, Number, String
            5. Edge Case Sensitivity: High, Medium, Low
            6. Algorithmic Pattern: Iteration, Recursion, Sorting, Searching, Set Operations, Conditional Logic
            7. Special Requirements: Order Preservation, Type Coercion, Mutability Constraints, Performance Constraints
            
            Format your response as a structured JSON-like dictionary with these keys.""",
            context=""
        )

        # Phase 2: Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break down the problem into essential subtasks with clear dependencies. Consider:
            - Input validation and type handling
            - Core algorithmic logic
            - Edge case identification and handling
            - Output formatting and type enforcement
            - Performance considerations
            - Potential failure points and validation checks
            
            Each subtask should be atomic and actionable. Include dependencies where one subtask relies on another's output.""",
            context=classification
        )

        # Phase 3: Parallel Analysis
        # Extract subtask descriptions for parallel processing
        subtask_descriptions = [subtask['description'] for subtask in decomposition]
        
        # Generate parallel analyses
        analysis_tasks = []
        for i, subtask in enumerate(subtask_descriptions):
            task = self.generate(
                instruction=f"""Address this specific subtask: {subtask}
                
                Guidelines:
                - Be specific and concrete
                - Include examples if helpful
                - Reference common Python patterns and pitfalls
                - Consider edge cases relevant to this subtask
                - Suggest implementation strategies
                
                Format your response as a clear, structured analysis with key points bulleted.""",
                context=f"Classification: {classification}"
            )
            analysis_tasks.append(task)
        
        parallel_analyses = await asyncio.gather(*analysis_tasks)

        # Phase 4: Ensemble Synthesis
        synthesis = await self.ensemble(
            instruction="""Synthesize all parallel analyses into a unified implementation plan. Your synthesis must:
            1. Resolve any contradictions between analyses by prioritizing robustness and specification compliance
            2. Create a step-by-step implementation guide that includes:
               - Exact function signature to implement
               - Core algorithmic approach
               - Edge case handling strategy
               - Data type management
               - Return value formatting
            3. Identify potential failure points and how to mitigate them
            4. Suggest validation strategies for the implementation
            
            Output a comprehensive, ready-to-implement plan that covers all aspects of the solution.""",
            contexts_list=parallel_analyses
        )

        # Phase 5: Code Generation
        implementation = await self.programmer(
            instruction="""Implement the function as specified in the original problem. Adhere strictly to:
            - The exact function signature
            - The implementation plan from the synthesis phase
            - All identified edge case handlers
            - Correct return type and data structure
            - Efficient algorithmic approach
            
            Include inline comments for complex logic. Ensure the code is clean, readable, and follows Python best practices.
            Handle all edge cases identified in the analysis phase. Validate input types if necessary.
            Return exactly what the problem specification requires - no more, no less.""",
            context=synthesis
        )

        # Phase 6: Iterative Revision (up to 3 iterations)
        current_implementation = implementation
        for iteration in range(3):
            critique = await self.revise(
                instruction=f"""Critically evaluate this implementation against the original problem specification:
                1. Does it handle all edge cases identified in the analysis phase?
                2. Is the return type exactly as specified?
                3. Are there any logical errors or boundary condition failures?
                4. Could the algorithm be more efficient or readable?
                5. Are there any Python-specific pitfalls (mutable defaults, type coercion, etc.)?
                
                If no issues are found, return "APPROVED" followed by the original code.
                If issues are found, return a revised version with fixes clearly commented.
                
                Current implementation:
                {current_implementation}""",
                context=f"Original Synthesis: {synthesis}"
            )
            
            if "APPROVED" in critique:
                break
            current_implementation = critique

        # Phase 7: Meta-Validation
        validation = await self.generate(
            instruction=f"""Perform final validation of this implementation:
            1. Create 3 novel test cases not shown in the original examples, focusing on edge conditions
            2. Mentally execute the code against these tests - does it pass?
            3. Verify that the implementation matches the exact function signature required
            4. Confirm that return types are correct in all cases
            5. Check for any remaining logical flaws or performance issues
            
            If validation passes, return "VALIDATED" followed by the final implementation.
            If validation fails, return "FAILED" with specific reasons.
            
            Implementation to validate:
            {current_implementation}""",
            context=f"Classification: {classification}\nSynthesis: {synthesis}"
        )

        # Extract final implementation (handle both VALIDATED and unvalidated cases)
        if "VALIDATED" in validation:
            final_implementation = validation.split("VALIDATED", 1)[-1].strip()
        elif "FAILED" in validation:
            # If validation failed, return the last revised version with a warning comment
            final_implementation = f"# VALIDATION FAILED - potential issues remain\n{current_implementation}"
        else:
            # Fallback: return the last revised version
            final_implementation = current_implementation

        return final_implementation