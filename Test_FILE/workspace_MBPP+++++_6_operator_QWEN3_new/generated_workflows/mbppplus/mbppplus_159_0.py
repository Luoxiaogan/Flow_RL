# Workflow ID: mbppplus_159_0
# Benchmark: mbppplus
# Data Indices: [56, 271]

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

        # Phase 1: Meta-Analysis - Understand problem nature and constraints
        problem_analysis = await self.generate(
            instruction="""Perform deep problem classification and constraint extraction:
            1. Determine primary category: mathematical, structural, logical, or hybrid.
            2. Identify all implicit constraints: input ranges, edge cases, output formats.
            3. Extract computational pitfalls: overflow risks, precision issues, performance bottlenecks.
            4. Note required transformations: input normalization, intermediate processing, output formatting.
            5. List potential solution strategies with their trade-offs.
            6. Predict 3-5 critical edge cases including empty inputs, boundary values, and degenerate structures.
            Present as structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation - Explore multiple solution angles
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop solution from MATHEMATICAL perspective:
                Problem Analysis: {problem_analysis}
                Focus on formulas, numerical methods, and algorithmic optimizations.
                Include handling of edge cases and computational constraints.
                Provide complete implementation strategy.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop solution from STRUCTURAL perspective:
                Problem Analysis: {problem_analysis}
                Focus on data structures, containment relationships, and transformation pipelines.
                Consider set operations, recursive patterns, and type preservation.
                Provide complete implementation strategy.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop solution from ALGORITHMIC perspective:
                Problem Analysis: {problem_analysis}
                Focus on step-by-step procedures, iteration patterns, and efficiency optimizations.
                Include complexity analysis and alternative approaches.
                Provide complete implementation strategy.""",
                context=problem_analysis
            )
        ]
        
        strategy_analyses = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Synthesis - Combine best elements from parallel analyses
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the most robust solution strategy:
            1. Compare mathematical, structural, and algorithmic approaches.
            2. Select elements that best handle edge cases and computational constraints.
            3. Ensure output format and type requirements are strictly met.
            4. Prioritize clarity, efficiency, and correctness.
            5. Create unified implementation plan with explicit steps.
            Return comprehensive strategy ready for code generation.""",
            contexts_list=strategy_analyses
        )

        # Phase 4: Code Generation with Edge Case Validation Loop
        max_attempts = 3
        code_solution = None
        edge_cases = await self.generate(
            instruction=f"""Generate 5 critical edge case test scenarios based on:
            Problem Analysis: {problem_analysis}
            Synthesized Strategy: {synthesized_strategy}
            Format as Python assert statements covering empty inputs, boundary values, and structural extremes.""",
            context=synthesized_strategy
        )

        for attempt in range(max_attempts):
            try:
                # Generate code implementation
                code_attempt = await self.programmer(
                    instruction=f"""Implement solution following this strategy:
                    {synthesized_strategy}
                    
                    Critical Requirements:
                    - Handle all edge cases from: {edge_cases}
                    - Match exact function signature from problem
                    - Include necessary imports
                    - Return correct data type
                    - No wrapper code or test cases
                    - Optimize for correctness over brevity""",
                    context=synthesized_strategy,
                    max_retries=1
                )
                
                # Validate code structure
                if "def " in code_attempt and not any(x in code_attempt for x in ["print(", "test", "assert"]):
                    code_solution = code_attempt
                    break
                    
                # If validation fails, revise strategy
                synthesized_strategy = await self.revise(
                    instruction=f"""Previous code attempt failed structural validation.
                    Error: Generated code contained invalid elements or missing function.
                    Revise strategy to emphasize:
                    1. Strict adherence to function signature
                    2. No test code or print statements
                    3. Proper import statements
                    4. Return statement with correct type
                    Original Strategy: {synthesized_strategy}""",
                    context=synthesized_strategy
                )
                
            except Exception as e:
                # On execution error, revise with error context
                synthesized_strategy = await self.revise(
                    instruction=f"""Code generation failed with error: {str(e)}
                    Revise strategy to address this failure.
                    Consider: input type handling, edge case coverage, algorithmic approach.
                    Previous Strategy: {synthesized_strategy}
                    Problem Analysis: {problem_analysis}""",
                    context=synthesized_strategy
                )

        # Phase 5: Final Code Refinement and Extraction
        if code_solution is None:
            # Fallback: direct generation with strongest constraints
            code_solution = await self.programmer(
                instruction=f"""Generate final solution with maximum constraints:
                Problem: {self.problem_text}
                Analysis: {problem_analysis}
                Strategy: {synthesized_strategy}
                Edge Cases: {edge_cases}
                
                ABSOLUTE REQUIREMENTS:
                - Function signature must exactly match problem
                - Include all necessary imports
                - Return correct data type
                - Handle all edge cases
                - No test code, print statements, or wrapper logic
                - Production-ready implementation""",
                context=synthesized_strategy,
                max_retries=1
            )

        # Extract clean function implementation
        final_code = await self.summarize(
            instruction="""Extract ONLY the function implementation:
            1. Remove any test cases, print statements, or wrapper code
            2. Ensure imports are included if used
            3. Preserve exact function signature
            4. Return only the function code as string
            5. No markdown, no explanations, no additional text""",
            context=code_solution
        )

        # Final validation and cleanup
        lines = final_code.strip().split('\n')
        clean_lines = []
        in_function = False
        
        for line in lines:
            if line.strip().startswith('def '):
                in_function = True
                clean_lines.append(line)
            elif in_function:
                if line.strip().startswith(('import ', 'from ')) and not any(cl.strip().startswith(('import ', 'from ')) for cl in clean_lines):
                    clean_lines.insert(0, line)  # Move imports to top
                elif not any(x in line for x in ['print(', 'test', 'assert', 'if __name__']):
                    clean_lines.append(line)
            elif line.strip().startswith(('import ', 'from ')) and not any(cl.strip().startswith(('import ', 'from ')) for cl in clean_lines):
                clean_lines.append(line)

        return '\n'.join(clean_lines)