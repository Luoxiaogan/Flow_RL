# Workflow ID: mbppplus_125_0
# Benchmark: mbppplus
# Data Indices: [318, 270]

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

        # Phase 1: Problem Decomposition - Extract core components
        decomposition = await self.decompose(
            instruction="""Break this programming problem into essential subproblems with clear dependencies. Focus on:
            1. Input type analysis: What data types are we handling? (lists, strings, numbers, etc.)
            2. Output specification: What exactly should be returned? (type, format, edge cases)
            3. Key operations: What transformations or algorithms are needed?
            4. Edge cases: What boundary conditions must be handled? (empty inputs, single elements, duplicates, type mismatches)
            5. Constraints: Any performance, memory, or implementation restrictions?
            Structure each subproblem with clear ID, description, and dependencies on other subproblems.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategy_tasks = [
            self.generate(
                instruction=f"""Propose a mathematical/algorithmic solution strategy:
                - Focus on formulaic or computational approaches
                - Consider time/space complexity
                - Handle edge cases identified in decomposition: {decomposition}
                - Prioritize correctness over elegance
                Provide detailed step-by-step reasoning.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose an iterative/transformative solution strategy:
                - Focus on loop-based or step-by-step processing
                - Consider state management and accumulators
                - Handle edge cases identified in decomposition: {decomposition}
                - Prioritize readability and maintainability
                Provide detailed implementation logic.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a functional/data-structure solution strategy:
                - Focus on using built-in functions, comprehensions, or data structure properties
                - Consider immutability and declarative approaches
                - Handle edge cases identified in decomposition: {decomposition}
                - Prioritize conciseness and Pythonic style
                Provide detailed transformation logic.""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all proposed strategies:
            - Identify complementary strengths: Which approach handles edge cases best? Which is most efficient?
            - Resolve conflicts: If strategies contradict, determine which is more correct based on problem constraints
            - Create unified approach: Combine elements into a single coherent solution plan
            - Add missing pieces: Ensure all edge cases from decomposition are addressed
            - Output should be a detailed, step-by-step implementation plan ready for coding""",
            contexts_list=strategy_results
        )

        # Phase 4: Code Generation with Self-Validation
        code_attempt = await self.programmer(
            instruction=f"""Generate Python code that implements the synthesized strategy:
            - Use EXACT function signature from problem
            - Include all necessary imports inside function if needed
            - Handle ALL edge cases identified in decomposition
            - Return correct data type (list vs tuple vs set)
            - Add inline comments for complex logic
            - Generate self-test assertions for key edge cases
            Strategy to implement: {synthesized_strategy}""",
            context=synthesized_strategy,
            max_retries=3
        )

        # Phase 5: Adaptive Refinement Loop
        current_code = code_attempt
        for iteration in range(3):
            # Validate and extract feedback
            validation_feedback = await self.generate(
                instruction=f"""Critically evaluate this code solution:
                - Does it handle all edge cases from decomposition: {decomposition}?
                - Is the return type correct?
                - Are there potential bugs or inefficiencies?
                - Does it match the problem's exact requirements?
                - If tests are included, do they cover critical cases?
                Provide specific, actionable feedback for improvement.""",
                context=current_code
            )
            
            # Check if validation is satisfied
            if any(phrase in validation_feedback.lower() for phrase in ["no issues", "all cases covered", "correct implementation"]):
                break
                
            # Revise code based on feedback
            current_code = await self.revise(
                instruction=f"""Improve the code based on this feedback:
                {validation_feedback}
                
                Specific requirements:
                - Maintain exact function signature
                - Fix identified bugs or edge cases
                - Preserve working functionality
                - Add necessary error handling
                - Keep code clean and readable""",
                context=current_code
            )

        # Phase 6: Final Standardization
        final_code = await self.revise(
            instruction="""Ensure code meets exact output requirements:
            - Function name matches problem exactly
            - Parameter names are correct
            - Return type is precisely as specified
            - No extra prints or debug statements
            - All imports are inside function if needed
            - Code is self-contained and ready for automated testing
            - Remove any test cases or example code not part of solution""",
            context=current_code
        )

        return final_code