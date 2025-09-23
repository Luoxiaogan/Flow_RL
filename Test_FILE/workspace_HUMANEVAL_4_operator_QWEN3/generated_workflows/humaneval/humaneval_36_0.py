# Workflow ID: humaneval_36_0
# Benchmark: humaneval
# Data Indices: [22, 30]

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

        # Step 1: Multi-perspective problem analysis in parallel
        analysis_tasks = [
            self.generate(
                instruction="""Perform detailed input-output pattern analysis:
                - Examine all provided examples in the docstring
                - Identify transformation patterns between input and output
                - Note any recurring operations (filtering, mapping, mathematical, string manipulation)
                - Extract explicit and implicit conditions
                - Identify edge cases demonstrated in examples (empty inputs, boundary values, mixed types)
                - Determine expected return type and structure
                Format your analysis as a structured report with clear sections.""",
                context=""
            ),
            self.generate(
                instruction="""Perform semantic interpretation of the docstring:
                - Paraphrase the problem description in your own words
                - Identify key verbs and nouns that define the operation
                - Determine the domain (numerical, string, list processing, algorithmic, etc.)
                - Infer the intent behind the examples
                - Highlight any constraints or special requirements mentioned
                - Suggest potential Python constructs that might be relevant (list comprehension, recursion, regex, etc.)
                Provide a comprehensive semantic breakdown.""",
                context=""
            ),
            self.generate(
                instruction="""Perform structural decomposition of examples:
                - For each example, break down the input into its components
                - Trace how each component contributes to the output
                - Identify invariants, conditions, or rules that must hold
                - Determine if the operation is stateless or requires accumulation
                - Assess whether the solution requires iteration, recursion, or direct computation
                - Note any type conversions or coercions implied by the examples
                Present your findings as a step-by-step structural analysis.""",
                context=""
            )
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Step 2: Synthesize analyses into unified problem characterization
        problem_characterization = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem characterization:
            - Identify consensus points across all analyses
            - Resolve any contradictions by prioritizing input-output pattern evidence
            - Classify the problem type with confidence (filtering, mapping, mathematical, string, algorithmic, etc.)
            - Extract the core operation or predicate that defines the transformation
            - List all identified edge cases that must be handled
            - Specify the exact return type and structure required
            - Recommend the most appropriate Python implementation strategy
            Produce a concise, actionable problem specification for code generation.""",
            contexts_list=analysis_results
        )

        # Step 3: Generate initial solution based on characterization
        initial_solution = await self.generate(
            instruction=f"""Generate Python code based on this problem characterization:
            {problem_characterization}
            
            Requirements:
            - Function name must match ENTRY POINT exactly
            - Return type must match examples precisely (int vs float, list vs tuple, etc.)
            - Handle all identified edge cases
            - Use the recommended implementation strategy
            - Code must be minimal and exactly match specification (no over-engineering)
            - Include no imports unless absolutely necessary (they will be auto-added if needed)
            
            Output ONLY the function implementation, nothing else.""",
            context=problem_characterization
        )

        # Step 4: Validation and revision loop (up to 3 iterations)
        current_solution = initial_solution
        for iteration in range(3):
            # Critique current solution
            critique = await self.generate(
                instruction=f"""Critically evaluate this solution against the original problem:
            {current_solution}
            
            Check for:
            - Correct function name matching ENTRY POINT
            - Alignment with all examples in docstring
            - Handling of identified edge cases
            - Correct return type and structure
            - Potential bugs or logical errors
            - Over-engineering or unnecessary complexity
            - Missing imports (if any are needed)
            
            If perfect, respond with 'APPROVED'.
            If flawed, provide specific, actionable feedback for improvement.""",
                context=current_solution
            )
            
            if "APPROVED" in critique.upper():
                break
                
            # Revise solution based on critique
            current_solution = await self.revise(
                instruction=f"""Revise the code based on this critique:
            {critique}
            
            Requirements:
            - Maintain exact function name
            - Fix all identified issues
            - Preserve correct return type
            - Keep code minimal and focused
            - Do not add functionality beyond specification
            
            Output ONLY the revised function implementation.""",
                context=current_solution
            )

        # Step 5: Final type and edge case alignment check
        final_check = await self.generate(
            instruction=f"""Perform final verification of this solution:
            {current_solution}
            
            Specifically check:
            - Return type matches examples exactly (if examples show integers, ensure no floats are returned)
            - All edge cases from examples are handled
            - No unnecessary type conversions
            - Function signature matches exactly
            
            If any issues found, provide minimal correction.
            If perfect, respond with 'FINAL_APPROVED'.""",
            context=current_solution
        )
        
        if "FINAL_APPROVED" not in final_check.upper():
            current_solution = await self.revise(
                instruction=f"""Apply these final corrections:
            {final_check}
            
            Output ONLY the corrected function implementation.""",
                context=current_solution
            )

        return current_solution