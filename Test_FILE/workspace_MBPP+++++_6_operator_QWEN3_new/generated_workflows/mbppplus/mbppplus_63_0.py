# Workflow ID: mbppplus_63_0
# Benchmark: mbppplus
# Data Indices: [52, 285]

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
        import json

        # Step 1: Decompose and classify the problem
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its core components. Identify:
            1. Input data structure and type (list, tuple, dict, etc.)
            2. Output data structure and type
            3. Primary operation (grouping, filtering, transforming, computing, etc.)
            4. Edge cases to consider (empty inputs, single elements, duplicates, type boundaries)
            5. Any implicit constraints from function signature or test cases
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Step 2: Generate problem classification summary
        classification = await self.generate(
            instruction=f"""Based on the decomposition:
            {json.dumps(decomposition, indent=2)}
            
            Classify this problem into one of these categories:
            - DICTIONARY_GROUPING: Building dicts from key-value pairs
            - NUMERIC_REDUCTION: Computing averages, sums, or other aggregates
            - STRING_MANIPULATION: Pattern matching, parsing, or formatting
            - SET_OPERATION: Union, intersection, difference of collections
            - LOGICAL_VALIDATION: Conditional processing or boolean outcomes
            
            Also extract:
            - Expected input type and structure
            - Expected output type and structure
            - Critical edge cases (empty, single, boundary)
            - Any type conversion requirements
            
            Format as JSON with keys: category, input_spec, output_spec, edge_cases, constraints""",
            context=json.dumps(decomposition)
        )

        # Step 3: Parallel solution generation along different axes
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on CORRECTNESS and EDGE CASES.
                Problem classification: {classification}
                
                Prioritize:
                - Handling empty inputs gracefully
                - Preserving exact output type (list vs tuple vs dict)
                - Avoiding type errors or index errors
                - Matching reference solution structure if available
                - Defensive programming with clear conditionals
                
                Return only the function implementation with necessary imports.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on EFFICIENCY and PYTHONIC STYLE.
                Problem classification: {classification}
                
                Prioritize:
                - Using appropriate data structures (defaultdict, Counter, etc.)
                - Minimizing unnecessary loops or copies
                - Leveraging built-in functions and comprehensions
                - Clean, readable variable names and structure
                - Following Python best practices
                
                Return only the function implementation with necessary imports.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on ROBUST TYPE HANDLING and STRUCTURE.
                Problem classification: {classification}
                
                Prioritize:
                - Explicit type checks or conversions if needed
                - Matching input/output structure exactly (tuple in, tuple out, etc.)
                - Handling mixed types or unexpected inputs gracefully
                - Preserving order when required
                - Documenting assumptions in code comments
                
                Return only the function implementation with necessary imports.""",
                context=classification
            )
        )

        # Step 4: Ensemble best solution from parallel attempts
        synthesized_solution = await self.ensemble(
            instruction="""Select and synthesize the best solution from the candidates below.
            Criteria:
            1. Correctness: Must handle edge cases (empty inputs, single elements)
            2. Type fidelity: Must match expected input/output types exactly
            3. Robustness: No unhandled exceptions or assumptions
            4. Readability: Clean, understandable code
            5. Efficiency: Reasonable algorithmic complexity
            
            If candidates have complementary strengths, merge them.
            Return ONLY the final function implementation with imports.""",
            contexts_list=solution_attempts
        )

        # Step 5: Validate with programmer operator (self-contained test scaffold)
        validation_result = await self.programmer(
            instruction=f"""Validate this solution against inferred constraints from classification:
            {classification}
            
            Generate minimal test cases including:
            - Empty input case
            - Single element case
            - Boundary values (0, negative, max/min)
            - Type consistency checks
            - Structure preservation checks
            
            Execute the code and return any errors or mismatches.
            If no errors, return 'VALIDATED'.""",
            context=synthesized_solution,
            max_retries=1
        )

        # Step 6: Conditional revision loop if validation fails
        current_solution = synthesized_solution
        if "VALIDATED" not in validation_result:
            for _ in range(2):  # Max 2 revision attempts
                revised = await self.revise(
                    instruction=f"""Fix the solution based on validation errors:
                    {validation_result}
                    
                    Critical requirements:
                    - MUST handle edge cases (especially empty inputs)
                    - MUST preserve exact return type
                    - MUST not crash on boundary values
                    - MUST match function signature exactly
                    
                    Return only the corrected function implementation.""",
                    context=current_solution
                )
                current_solution = revised
                
                # Re-validate
                revalidation = await self.programmer(
                    instruction="Revalidate the revised solution with same test cases.",
                    context=current_solution,
                    max_retries=1
                )
                if "VALIDATED" in revalidation:
                    break

        # Step 7: Final self-reflection and type consistency check
        final_check = await self.summarize(
            instruction=f"""Summarize the core logic and invariants of this solution:
            {current_solution}
            
            Verify against original problem:
            - Does return type match? (dict, list, float, etc.)
            - Are all edge cases handled?
            - Is the algorithm logically sound?
            - Any type coercion or structure mismatches?
            
            If any mismatch, flag it. Otherwise, return 'CONSISTENT'.""",
            context=current_solution
        )

        # Final output
        if "CONSISTENT" not in final_check and "VALIDATED" in validation_result:
            # If reflection finds issue but validation passed, return revised version
            return current_solution
        elif "CONSISTENT" in final_check:
            return current_solution
        else:
            # Fallback: return the synthesized solution if all else fails
            return synthesized_solution