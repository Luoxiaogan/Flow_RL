# Workflow ID: humaneval_22_0
# Benchmark: humaneval
# Data Indices: [108, 129]

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

        # Phase 1: Multi-perspective problem analysis (Diamond Pattern)
        analysis_instructions = [
            """Analyze the problem from a MATHEMATICAL perspective:
            - Identify numerical patterns, formulas, or transformations
            - Extract any arithmetic, algebraic, or logical relationships
            - Note how inputs map to outputs in the examples
            - Highlight any invariants or constraints
            - Format as structured bullet points""",
            
            """Analyze the problem from a STRUCTURAL perspective:
            - Identify data types and structures involved (lists, grids, strings, etc.)
            - Note traversal patterns, neighbor relationships, or access patterns
            - Extract size constraints, boundary conditions, or grid properties
            - Highlight any spatial or topological relationships
            - Format as structured bullet points""",
            
            """Analyze the problem from an EDGE CASE perspective:
            - Identify all edge cases demonstrated in examples (empty inputs, zeros, negatives, singles)
            - Infer unstated edge cases that might exist
            - Note special handling rules mentioned in docstring
            - Highlight return type requirements (int vs float, list vs scalar)
            - Format as structured bullet points"""
        ]

        # Parallel analysis from multiple perspectives
        analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in analysis_instructions]
        )

        # Merge analyses into unified understanding
        unified_analysis = await self.ensemble(
            instruction="""Synthesize all perspectives into a unified problem specification:
            - Combine mathematical patterns with structural constraints
            - Integrate edge case handling requirements
            - Extract precise return type from examples
            - Formulate the core algorithmic rule in plain English
            - Identify any hidden invariants or optimization opportunities
            - Output as a comprehensive specification document""",
            contexts_list=analyses
        )

        # Extract function signature and entry point
        signature_extraction = await self.generate(
            instruction="""From the original problem, extract EXACTLY:
            - The function name (ENTRY POINT)
            - Parameter names and types
            - Return type (inferred from examples)
            Format as: "def function_name(param1, param2) -> ReturnType:"""",
            context=""
        )

        # Phase 2: Generate initial solution with injected constraints
        initial_solution = await self.generate(
            instruction=f"""Generate Python code that implements the function based on this specification:
            {unified_analysis}
            
            STRICT REQUIREMENTS:
            - Function name MUST match: {signature_extraction}
            - Return type MUST match examples (int, float, list, etc.)
            - Handle ALL edge cases identified in analysis
            - Code must be minimal and precise - no over-engineering
            - Include NO imports (they will be auto-added)
            - Return ONLY the function definition, nothing else
            
            THINK STEP BY STEP:
            1. Restate the core algorithm in one sentence
            2. Outline the implementation steps
            3. Write the code with careful attention to edge cases
            4. Verify against examples mentally""",
            context=unified_analysis
        )

        # Phase 3: Iterative refinement with simulated validation
        current_solution = initial_solution
        for iteration in range(3):  # Max 3 revision cycles
            # Validate against examples (simulated)
            validation = await self.generate(
                instruction=f"""Simulate executing this code against ALL examples in the docstring:
                Code: {current_solution}
                
                For each example:
                - Show input → expected output (from docstring)
                - Show computed output (by reasoning through code)
                - Note any mismatches
                - Identify specific lines causing errors
                - Suggest precise fixes
                
                If no mismatches, output "VALID: Ready for submission"
                Otherwise, output detailed revision instructions""",
                context=current_solution
            )

            if "VALID" in validation and "Ready for submission" in validation:
                break

            # Revise based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Fix the code based on this validation feedback:
                {validation}
                
                CRITICAL RULES:
                - Preserve function signature exactly
                - Maintain correct return type
                - Handle all edge cases
                - Make minimal changes necessary
                - Return ONLY the function definition""",
                context=current_solution
            )

        # Final output type enforcement
        final_solution = await self.revise(
            instruction="""Ensure the code meets these final requirements:
            - Function name matches ENTRY POINT exactly
            - Return type matches examples precisely (int vs float matters)
            - No extraneous code or comments
            - Clean, minimal implementation
            - Return ONLY the function definition, nothing else""",
            context=current_solution
        )

        return final_solution