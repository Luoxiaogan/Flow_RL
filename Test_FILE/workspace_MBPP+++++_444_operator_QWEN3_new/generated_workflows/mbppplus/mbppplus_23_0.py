# Workflow ID: mbppplus_23_0
# Benchmark: mbppplus
# Data Indices: [23, 3, 283]

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
        
        # Phase 1: Comprehensive Problem Specification Extraction
        specification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and extract a complete formal specification. Your analysis must include:

1. FUNCTION SIGNATURE: Extract the exact function name and parameter names/types from the problem. Preserve case and spelling exactly.

2. INPUT/OUTPUT CONTRACT: 
   - What are the expected input types and constraints?
   - What is the expected output type and format?
   - Are there any implicit type conversions required?

3. EDGE CASES: Identify at least 5 potential edge cases including:
   - Empty inputs (empty strings, empty lists, etc.)
   - Single element inputs
   - Boundary values (minimum/maximum values, first/last positions)
   - Invalid or unexpected inputs
   - Duplicate elements (if applicable)

4. TRANSFORMATION RULES: 
   - What exact transformation must be applied to inputs to produce outputs?
   - Are there any mathematical formulas, algorithms, or logical operations required?
   - What are the step-by-step operations needed?

5. VALIDATION CRITERIA:
   - What constitutes a correct solution?
   - What are common failure modes to avoid?
   - What test cases would reveal implementation errors?

Format your response as a structured specification with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation - Three Distinct Approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a DIRECT implementation based on the specification:
{specification}

Guidelines:
- Focus on clarity and straightforward implementation
- Use the most obvious approach that directly maps specification to code
- Don't optimize prematurely - prioritize correctness and readability
- Include comments explaining key steps
- Handle edge cases explicitly as identified in specification
- Return the complete function implementation with imports""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate an OPTIMIZED implementation based on the specification:
{specification}

Guidelines:
- Focus on efficiency and performance
- Use the most computationally efficient approach
- Consider algorithmic complexity and memory usage
- Use built-in functions and libraries where appropriate
- Include comments explaining optimization choices
- Handle edge cases with minimal overhead
- Return the complete function implementation with imports""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate a DEFENSIVE implementation based on the specification:
{specification}

Guidelines:
- Focus on robustness and error handling
- Validate inputs and handle edge cases comprehensively
- Include type checking and boundary validation
- Use try-catch blocks where appropriate
- Include detailed comments explaining defensive measures
- Return the complete function implementation with imports""",
                context=specification
            )
        )

        # Phase 3: Synthesize Best Elements from All Approaches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a final solution by combining the best elements from all three approaches:

1. CLARITY: Take the clearest, most readable code structure from the DIRECT implementation.

2. EFFICIENCY: Incorporate the most efficient algorithms and optimizations from the OPTIMIZED implementation.

3. ROBUSTNESS: Integrate the most comprehensive error handling and edge case management from the DEFENSIVE implementation.

4. CODE QUALITY: 
   - Ensure proper formatting and Pythonic style
   - Include only necessary imports
   - Add concise, helpful comments
   - Remove any redundant or conflicting code

5. VALIDATION: Verify that the synthesized solution:
   - Matches the exact function signature required
   - Handles all identified edge cases
   - Produces correct output for sample inputs
   - Is free of syntax errors

Return ONLY the complete, synthesized function implementation with necessary imports. Do not include any additional text or explanations.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Validation and Iterative Refinement
        current_solution = synthesized_solution
        max_iterations = 3
        
        for iteration in range(max_iterations):
            # Generate validation test cases
            validation_analysis = await self.generate(
                instruction=f"""Generate comprehensive validation for this solution:
{current_solution}

Based on the original problem specification:
{specification}

Create:
1. 5 TEST CASES that cover:
   - Normal cases (from problem examples)
   - Edge cases (from specification)
   - Boundary conditions
   - Potential failure points
   - Unexpected inputs

2. For each test case, predict the expected output.

3. Identify any potential issues with the current implementation including:
   - Logic errors
   - Edge case handling gaps
   - Type mismatches
   - Performance bottlenecks
   - Style or readability issues

Format as: "TEST CASES: [list of test cases with expected outputs]
ISSUES: [list of identified issues or 'NONE' if perfect]" """,
                context=current_solution
            )

            # Check if validation found issues
            if "ISSUES: NONE" in validation_analysis or "no issues" in validation_analysis.lower() or "perfect" in validation_analysis.lower():
                break
            
            # Revise solution based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix all identified issues:

Validation feedback:
{validation_analysis}

Original specification:
{specification}

Revision requirements:
1. Fix all identified issues while preserving core functionality
2. Maintain the exact function signature
3. Keep code clean and well-commented
4. Ensure all edge cases are properly handled
5. Return ONLY the complete revised function implementation with necessary imports""",
                context=current_solution
            )

        # Final cleanup and formatting pass
        final_solution = await self.revise(
            instruction="""Perform final cleanup and ensure perfect formatting:

1. Verify the function signature matches exactly what's required
2. Ensure all necessary imports are included at the top
3. Remove any unnecessary comments or code
4. Format code according to Python best practices
5. Ensure no syntax errors
6. Return ONLY the clean, final function implementation with imports""",
            context=current_solution
        )

        return final_solution