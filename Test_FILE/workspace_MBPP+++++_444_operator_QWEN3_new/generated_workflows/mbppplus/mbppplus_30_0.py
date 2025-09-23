# Workflow ID: mbppplus_30_0
# Benchmark: mbppplus
# Data Indices: [76, 182, 55]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Phase 1: Parallel problem analysis from multiple perspectives
        analysis_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL perspective:
                - Identify all numerical relationships, formulas, or equations involved
                - Determine if exact calculations or approximations are needed
                - Note any mathematical constraints or invariants
                - Specify required precision and rounding rules
                - Format output as a structured markdown list""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an ALGORITHMIC perspective:
                - Identify the core algorithm or data structure needed
                - Determine time/space complexity requirements
                - Note any sorting, searching, or transformation steps
                - Specify iteration/recursion patterns
                - Format output as a structured markdown list""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an EDGE CASE perspective:
                - Identify all possible boundary conditions
                - Consider empty inputs, single elements, duplicates, negatives
                - Note type conversion requirements (int/float/string)
                - Specify return type expectations (list vs tuple vs set)
                - Format output as a structured markdown list""",
                context=""
            )
        ]
        analyses = await asyncio.gather(*analysis_tasks)

        # Phase 2: Synthesize analyses into unified implementation plan
        implementation_plan = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified implementation plan:
            - Resolve contradictions by prioritizing mathematical correctness
            - Combine algorithmic steps with edge case handling
            - Specify exact function signature and return type
            - Include explicit handling of all identified edge cases
            - Outline step-by-step implementation logic
            - Format as executable pseudocode with type annotations""",
            contexts_list=analyses
        )

        # Phase 3: Generate two implementation variants
        implementation_tasks = [
            self.generate(
                instruction=f"""Generate a CLEAR and CORRECT implementation based on this plan:
                {implementation_plan}
                
                Requirements:
                - Prioritize readability and correctness over optimization
                - Include explicit type handling and edge case checks
                - Use descriptive variable names
                - Match exact function signature from problem
                - Return correct data type as specified in edge case analysis
                - Format as pure Python code with no markdown""",
                context=implementation_plan
            ),
            self.generate(
                instruction=f"""Generate an EFFICIENT and ROBUST implementation based on this plan:
                {implementation_plan}
                
                Requirements:
                - Prioritize computational efficiency and minimal edge case overhead
                - Use optimal data structures and algorithms
                - Include defensive programming for unexpected inputs
                - Match exact function signature from problem
                - Return correct data type as specified in edge case analysis
                - Format as pure Python code with no markdown""",
                context=implementation_plan
            )
        ]
        implementations = await asyncio.gather(*implementation_tasks)

        # Phase 4: Cross-revise implementations
        revised_implementations = []
        for i, impl in enumerate(implementations):
            other_impl = implementations[1 - i]  # Get the other implementation
            revised = await self.revise(
                instruction=f"""Critically revise this implementation by comparing with the alternative:
                Alternative implementation:
                {other_impl}
                
                Requirements:
                - Identify missing edge cases or type handling
                - Fix any logical gaps or mathematical errors
                - Improve clarity without sacrificing correctness
                - Ensure function signature matches problem exactly
                - Preserve the core approach but incorporate best elements from alternative
                - Format as pure Python code with no markdown""",
                context=impl
            )
            revised_implementations.append(revised)

        # Phase 5: Generate test cases and validate implementations
        test_cases = await self.generate(
            instruction="""Generate 3 comprehensive test cases for this problem:
            - 1 typical case (normal inputs)
            - 1 edge case (boundary conditions, empty inputs, etc.)
            - 1 adversarial case (unexpected inputs, maximum values, etc.)
            
            Format each test case as:
            assert function_name(...) == expected_output
            Include comments explaining each test case""",
            context=implementation_plan
        )

        # Validate each implementation against test cases
        validation_tasks = []
        for impl in revised_implementations:
            validation = await self.revise(
                instruction=f"""Validate this implementation against these test cases:
                {test_cases}
                
                Requirements:
                - Predict output for each test case
                - Flag any test cases that would fail or crash
                - Identify specific lines causing issues
                - Suggest fixes for failing test cases
                - Rate confidence in implementation (1-10)
                - Format as structured analysis with clear pass/fail indicators""",
                context=impl
            )
            validation_tasks.append(validation)
        
        validations = await asyncio.gather(*validation_tasks)

        # Phase 6: Final ensemble selection
        final_implementation = await self.ensemble(
            instruction="""Select the best implementation based on validation results:
            - Prefer implementation that passes all test cases
            - If both pass, choose the one with simpler logic
            - If neither passes, synthesize a hybrid that fixes all identified issues
            - Ensure final code matches exact function signature from problem
            - Include all necessary imports at top
            - Format as pure Python code with no markdown or comments beyond imports""",
            contexts_list=[f"Implementation:\n{impl}\n\nValidation:\n{val}" 
                          for impl, val in zip(revised_implementations, validations)]
        )

        # Phase 7: Confidence check and optional refinement
        confidence_check = await self.generate(
            instruction=f"""Rate confidence in this final implementation (1-10):
            {final_implementation}
            
            Consider:
            - Completeness of edge case handling
            - Correctness of mathematical/logical operations
            - Type consistency and return value matching
            - Readability and maintainability
            - Only output a single number (1-10)""",
            context=final_implementation
        )

        try:
            confidence_score = int(confidence_check.strip())
        except ValueError:
            confidence_score = 5  # Default if parsing fails

        if confidence_score < 8:
            # Extract weakest component and refine
            weak_point = await self.generate(
                instruction=f"""Identify the single most fragile component of this implementation:
                {final_implementation}
                
                Consider:
                - Most likely to fail edge cases
                - Most complex or unclear logic
                - Most prone to type errors
                - Output only the specific code section needing improvement""",
                context=final_implementation
            )
            
            final_implementation = await self.revise(
                instruction=f"""Strengthen this fragile component with enhanced robustness:
                {weak_point}
                
                Requirements:
                - Add explicit edge case handling
                - Improve type safety
                - Simplify complex logic if possible
                - Maintain exact function signature
                - Integrate seamlessly with rest of implementation
                - Format as pure Python code with no markdown""",
                context=final_implementation
            )

        return final_implementation