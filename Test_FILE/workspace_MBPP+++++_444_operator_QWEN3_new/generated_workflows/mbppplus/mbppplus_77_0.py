# Workflow ID: mbppplus_77_0
# Benchmark: mbppplus
# Data Indices: [124, 285, 295]

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

        # Phase 1: Problem Classification and Requirement Extraction
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:

1. Classify the problem type (string manipulation, numerical computation, data structure transformation, etc.)
2. Identify expected input and output data types (list, tuple, string, number, etc.)
3. Extract key operations required (searching, sorting, filtering, mathematical operations, pattern matching, etc.)
4. Identify potential edge cases (empty inputs, single elements, duplicates, boundary values, type conversions)
5. Determine if any specific Python modules are likely needed (re, math, etc.)
6. Note any constraints on return types or function signatures
7. Summarize the core challenge in one sentence

Present your analysis in a structured format with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python solution based on this analysis:
{problem_analysis}

Strategy 1: Focus on simplicity and readability. Use built-in Python functions where possible. Prioritize clear, straightforward code over clever optimizations. Include necessary imports at the top of the function body.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution based on this analysis:
{problem_analysis}

Strategy 2: Focus on robustness and edge case handling. Explicitly handle empty inputs, type conversions, and boundary conditions. Add defensive programming checks where appropriate. Ensure return type exactly matches requirements.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution based on this analysis:
{problem_analysis}

Strategy 3: Focus on efficiency and Pythonic idioms. Use list comprehensions, generator expressions, or functional programming constructs where appropriate. Consider performance implications for large inputs. Use most appropriate data structures for the task.""",
                context=problem_analysis
            )
        )

        # Phase 3: Parallel Solution Critique
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically evaluate this solution:

1. Does it handle all edge cases mentioned in the problem analysis?
2. Does it use the correct function signature and parameter names?
3. Does it return the exact expected data type?
4. Are all necessary imports included?
5. Is there any potential for off-by-one errors, type mismatches, or other common bugs?
6. Does it match the requirements shown in any test cases?
7. Suggest specific improvements or corrections.

Be brutally honest - point out even minor issues.""",
                context=candidate
            ) for candidate in solution_candidates]
        )

        # Phase 4: Solution Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Revise this solution based on the following critique:
{critique}

Make all necessary corrections while preserving the core approach. Ensure:
- Function signature matches exactly
- All imports are included
- Edge cases are properly handled
- Return type is correct
- Code is clean and readable

Return only the complete, corrected Python code with no additional commentary.""",
                context=solution_candidates[i]
            ) for i, critique in enumerate(critiques)]
        )

        # Phase 5: Solution Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best aspects of these refined solutions into a final implementation:

1. Choose the solution that best handles edge cases and matches requirements
2. Incorporate any superior approaches or optimizations from the other solutions
3. Ensure the function signature is exactly as specified
4. Verify all necessary imports are included
5. Confirm the solution is robust, efficient, and readable
6. Return ONLY the complete Python code with no additional text or commentary

The final solution must be production-ready and pass all test cases including edge cases.""",
            contexts_list=refined_solutions
        )

        # Phase 6: Final Validation and Cleanup
        validated_solution = await self.revise(
            instruction="""Perform final validation of this solution:

1. Verify function signature matches exactly what was requested
2. Ensure all imports are present and correct
3. Check that return type matches requirements
4. Confirm no placeholder code or TODO comments remain
5. Ensure code is properly formatted with consistent indentation
6. Remove any unnecessary comments or debug statements

Return ONLY the final, cleaned Python code with no additional text.""",
            context=final_solution
        )

        return validated_solution