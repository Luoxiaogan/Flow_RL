# Workflow ID: mbppplus_89_0
# Benchmark: mbppplus
# Data Indices: [243, 343]

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
        
        # Phase 1: Problem Classification and Intent Extraction
        classification = await self.generate(
            instruction="""Comprehensive Problem Analysis:
            1. CLASSIFY the problem type: Is it mathematical, string manipulation, array/list processing, or logical?
            2. IDENTIFY key constraints: What are the input/output types? Any boundary conditions? Edge cases to consider?
            3. EXTRACT core requirements: What exactly must the solution accomplish? What would constitute failure?
            4. ENUMERATE at least two potential solution approaches with their trade-offs (time complexity, space complexity, implementation difficulty)
            5. FLAG any ambiguities or missing information in the problem statement
            6. PREDICT likely edge cases: empty inputs, single elements, maximum/minimum values, type mismatches
            7. DETERMINE if this is a trivial problem (can be solved in 1-2 lines) or requires complex logic
            Present your analysis in structured format with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Analysis - Three Perspectives
        math_analysis, practical_analysis, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction="""MATHEMATICAL/FORMAL ANALYSIS:
                - Derive any mathematical formulas or theoretical foundations
                - Identify patterns, sequences, or algebraic relationships
                - Consider closed-form solutions vs. iterative approaches
                - Analyze time/space complexity theoretically
                - Look for mathematical optimizations or shortcuts
                Base your analysis on this classification: """ + classification,
                context=classification
            ),
            self.generate(
                instruction="""PRACTICAL IMPLEMENTATION ANALYSIS:
                - Outline step-by-step pseudocode for the most straightforward approach
                - Consider data structures needed and their operations
                - Identify potential implementation pitfalls (off-by-one errors, type conversions, etc.)
                - Suggest variable names and code structure that match problem semantics
                - Note any library functions or built-ins that could simplify implementation
                Base your analysis on this classification: """ + classification,
                context=classification
            ),
            self.generate(
                instruction="""EDGE CASE & ROBUSTNESS ANALYSIS:
                - List ALL possible edge cases (empty inputs, single elements, duplicates, boundary values)
                - For each edge case, specify expected behavior and how to handle it
                - Consider input validation requirements (if any)
                - Identify potential failure points in implementation
                - Suggest defensive programming techniques to ensure robustness
                Base your analysis on this classification: """ + classification,
                context=classification
            )
        )

        # Phase 3: Synthesis and Strategy Selection
        synthesized_strategy = await self.ensemble(
            instruction="""SYNTHESIZE A COMPREHENSIVE SOLUTION STRATEGY:
            You have three analyses of the problem:
            1. Mathematical/Formal Analysis
            2. Practical Implementation Analysis  
            3. Edge Case & Robustness Analysis

            Your task:
            - INTEGRATE the strongest elements from each analysis into a unified approach
            - RESOLVE any conflicts between analyses (e.g., if math suggests O(1) but practical suggests O(n))
            - PRIORITIZE correctness and robustness over theoretical optimality
            - CREATE a detailed implementation plan that addresses all edge cases
            - SPECIFY exact function signature, parameter handling, and return type
            - INCLUDE comments explaining how edge cases are handled
            - DECIDE whether to use mathematical optimization or straightforward implementation based on problem context
            The output should be a complete blueprint for code implementation.""",
            contexts_list=[math_analysis, practical_analysis, edge_case_analysis]
        )

        # Phase 4: Iterative Implementation and Validation
        current_implementation = None
        max_retries = 3
        
        for iteration in range(max_retries):
            # Generate code implementation
            if iteration == 0:
                implementation_context = synthesized_strategy
            else:
                implementation_context = f"Previous attempt (iteration {iteration}):\n{current_implementation}\n\nFeedback from validation:\n{validation_feedback}\n\nRevised strategy:\n{revised_strategy}"
            
            current_implementation = await self.programmer(
                instruction=f"""IMPLEMENT THE SOLUTION:
                Follow this strategy exactly: {synthesized_strategy}
                
                Requirements:
                - Use EXACT function name and signature from problem
                - Handle ALL edge cases identified in analysis
                - Include comments explaining edge case handling
                - Return correct data type (match problem specification)
                - Code must be self-contained (include necessary imports)
                - Prioritize clarity and correctness over cleverness
                - Test your code mentally against edge cases before finalizing
                
                IMPORTANT: The solution must be robust enough to pass extensive test suites including edge cases not shown in examples.""",
                context=implementation_context,
                max_retries=1
            )

            # Validate implementation
            validation_feedback = await self.generate(
                instruction="""CRITICALLY REVIEW THIS IMPLEMENTATION:
                - Check for off-by-one errors
                - Verify type consistency (input/output types)
                - Test edge cases mentally: empty inputs, single elements, boundary values
                - Look for logical errors or incorrect assumptions
                - Check variable initialization and loop conditions
                - Verify return type matches problem requirements
                - Identify any potential runtime errors
                - Suggest specific improvements or fixes
                If no issues found, state "VALID: No issues detected" clearly at the beginning.""",
                context=current_implementation
            )

            # Check if validation passed
            if "VALID: No issues detected" in validation_feedback:
                break
            elif iteration < max_retries - 1:
                # Revise strategy based on feedback
                revised_strategy = await self.revise(
                    instruction=f"""REVISE IMPLEMENTATION STRATEGY BASED ON FEEDBACK:
                    Original strategy: {synthesized_strategy}
                    Validation feedback: {validation_feedback}
                    
                    Requirements:
                    - Address ALL issues raised in feedback
                    - Maintain core approach but fix specific problems
                    - Keep edge case handling intact while fixing bugs
                    - If feedback suggests fundamental flaw, consider alternative approach from original analyses
                    - Output revised complete implementation strategy""",
                    context=synthesized_strategy
                )
                synthesized_strategy = revised_strategy

        return current_implementation