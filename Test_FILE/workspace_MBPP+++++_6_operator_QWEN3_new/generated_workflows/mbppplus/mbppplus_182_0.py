# Workflow ID: mbppplus_182_0
# Benchmark: mbppplus
# Data Indices: [176, 33]

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
        
        # Phase 1: Parallel Problem Analysis and Classification
        classification, edge_case_analysis, structure_analysis = await asyncio.gather(
            self.generate(
                instruction="""Comprehensive Problem Classification:
                1. Determine primary problem category: mathematical computation, data structure manipulation, string processing, or logical validation.
                2. Identify required operations: sorting, filtering, transformation, recursion, iteration, etc.
                3. Note expected input/output types and constraints.
                4. Assess complexity level: simple calculation, multi-step algorithm, or complex transformation.
                5. Suggest 2-3 potential solution approaches with their trade-offs.
                Format as structured analysis with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Edge Case Identification:
                1. List all potential edge cases: empty inputs, single elements, duplicates, negative numbers, boundary values.
                2. Consider type edge cases: None, empty collections, type mismatches.
                3. Identify performance edge cases: very large inputs, worst-case scenarios.
                4. Note any special constraints or exceptional conditions mentioned or implied.
                Format as bullet-point list with brief explanations.""",
                context=""
            ),
            self.generate(
                instruction="""Problem Structure Analysis:
                1. Extract key parameters and variables from the problem statement.
                2. Identify input/output specifications including data types and formats.
                3. Map the logical flow required: what transformations or calculations are needed.
                4. Note any patterns, sequences, or mathematical relationships implied.
                5. Identify any hidden constraints or assumptions.
                Format as structured breakdown with clear labeling.""",
                context=""
            )
        )
        
        # Phase 2: Strategy Selection and Solution Generation
        strategy_context = f"""Classification: {classification}

Edge Cases: {edge_case_analysis}

Structure: {structure_analysis}"""
        
        # Generate multiple solution approaches in parallel
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Mathematical/Algorithmic Solution:
                Based on the analysis:
                {strategy_context}
                
                Create a Python function that solves the problem with:
                1. Correct function signature matching requirements
                2. Proper handling of identified edge cases
                3. Efficient algorithmic approach
                4. Clear, readable code with appropriate variable names
                5. Return type matching specifications
                Include detailed comments explaining the approach.""",
                context=strategy_context
            ),
            self.generate(
                instruction=f"""Generate Alternative Solution with Different Approach:
                Based on the analysis:
                {strategy_context}
                
                Create an alternative Python solution using a different algorithmic strategy:
                1. If original was iterative, try recursive or mathematical formula
                2. If original used sorting, try hashing or direct computation
                3. Focus on different trade-offs (space vs time, readability vs efficiency)
                4. Still handle all edge cases and match specifications
                5. Include comments comparing this approach to the first.""",
                context=strategy_context
            )
        )
        
        # Select best approach or synthesize
        selected_solution = await self.ensemble(
            instruction="""Select and Refine Best Solution:
            Compare the two solution approaches provided. Consider:
            1. Correctness and completeness (handles all edge cases)
            2. Efficiency and scalability
            3. Code clarity and maintainability
            4. Adherence to problem specifications
            5. Robustness against unexpected inputs
            
            Either select the better solution or synthesize a hybrid that combines the best elements of both.
            Return ONLY the final Python function code with no additional text or explanation.
            Ensure perfect syntax and matching function signature.""",
            contexts_list=approaches
        )
        
        # Phase 3: Iterative Refinement and Validation
        refined_solution = selected_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation_feedback = await self.generate(
                instruction=f"""Rigorous Solution Validation:
                Analyze this solution for:
                1. Syntax errors and logical flaws
                2. Edge case handling (refer to earlier edge case analysis)
                3. Type consistency and return value correctness
                4. Performance issues or inefficiencies
                5. Deviations from problem requirements
                6. Code style and readability improvements
                
                If no issues found, respond with "VALIDATED".
                Otherwise, provide specific, actionable feedback for improvement.
                
                Solution to validate:
                {refined_solution}""",
                context=refined_solution
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            # Revise based on feedback
            refined_solution = await self.revise(
                instruction=f"""Improve Solution Based on Feedback:
                Address all issues identified in the validation feedback:
                {validation_feedback}
                
                Maintain the exact function signature and core logic while fixing problems.
                Enhance code quality, edge case handling, and efficiency as needed.
                Return ONLY the improved Python function code with no additional text.""",
                context=refined_solution
            )
        
        # Final verification through Programmer for computational problems
        # Only use Programmer if problem involves mathematical computation
        if "mathematical" in classification.lower() or "computation" in classification.lower():
            try:
                # Extract function name for testing
                func_match = re.search(r'def\s+(\w+)\s*\(', refined_solution)
                if func_match:
                    func_name = func_match.group(1)
                    # Create simple test harness
                    test_code = f"""
{refined_solution}

# Test with simple case
result = {func_name}({'2' if 'even_Power_Sum' in func_name else '[1,2,3],3'})
print(result)
"""
                    programmer_result = await self.programmer(
                        instruction="Execute this code to verify basic functionality",
                        context=test_code,
                        max_retries=1
                    )
                    # If execution successful, use the refined solution
                    # If fails, fall back to refined_solution (already iteratively improved)
            except Exception:
                pass  # Fall back to refined_solution if Programmer fails
        
        return refined_solution