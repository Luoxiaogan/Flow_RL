# Workflow ID: humaneval_4_0
# Benchmark: humaneval
# Data Indices: [14, 35]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Sophisticated universal workflow for code generation from specifications.
        Combines parallel analysis, conditional strategy selection, iterative refinement, 
        and ensemble synthesis to handle any problem in this domain.
        """
        import asyncio
        
        # Phase 1: Parallel multi-perspective problem analysis
        analysis_tasks = [
            self.generate(
                instruction="""Perform deep structural analysis of the problem:
                1. Identify the core operation being requested (e.g., transformation, aggregation, generation)
                2. Extract all explicit and implicit constraints from examples
                3. Determine input/output types and edge cases (empty input, single element, boundary values)
                4. Recognize patterns in the examples (incremental, comparative, recursive, etc.)
                5. Classify problem type: mathematical, string manipulation, list processing, algorithmic, etc.
                6. Suggest 2-3 potential implementation approaches with pros/cons
                Be thorough and systematic. Consider what's NOT shown in examples but might be tested.""",
                context=""
            ),
            self.generate(
                instruction="""Focus exclusively on edge case detection:
                1. What edge cases are demonstrated in the examples?
                2. What edge cases are likely but not shown? (empty inputs, single elements, extreme values, duplicates, etc.)
                3. What would cause the function to fail based on the specification?
                4. What boundary conditions exist?
                5. How should type conversions or precision be handled?
                6. Are there any hidden assumptions in the examples?
                List all potential edge cases systematically.""",
                context=""
            ),
            self.generate(
                instruction="""Pattern recognition and algorithm identification:
                1. What algorithmic pattern does this problem follow? (sliding window, two pointers, recursion, etc.)
                2. What data structures are implied by the examples?
                3. Is this a known problem type with standard solutions?
                4. What is the time/space complexity expectation based on examples?
                5. Are there mathematical formulas or properties that could simplify the solution?
                6. Can this be solved with built-in Python functions or does it require custom logic?
                Provide specific algorithmic recommendations.""",
                context=""
            )
        ]
        
        # Execute parallel analysis
        structural_analysis, edge_case_analysis, pattern_analysis = await asyncio.gather(*analysis_tasks)
        
        # Phase 2: Conditional strategy selection based on problem type
        problem_classification = await self.generate(
            instruction=f"""Based on the following analyses, classify this problem and select the optimal strategy:
            
            Structural Analysis: {structural_analysis}
            Edge Case Analysis: {edge_case_analysis}
            Pattern Analysis: {pattern_analysis}
            
            Classification Criteria:
            1. Primary category: string, list, mathematical, algorithmic, or other
            2. Complexity level: simple transformation, moderate logic, complex algorithm
            3. Key implementation approach: iteration, recursion, built-in functions, mathematical formula, etc.
            4. Critical edge cases to handle
            5. Recommended variable naming and code structure
            
            Output format:
            CATEGORY: [category]
            APPROACH: [recommended approach]
            EDGE_CASES: [comma-separated list of critical edge cases]
            IMPLEMENTATION_NOTES: [specific guidance for implementation]""",
            context=f"{structural_analysis}\n\n{edge_case_analysis}\n\n{pattern_analysis}"
        )
        
        # Phase 3: Parallel solution generation from different perspectives
        solution_tasks = [
            self.generate(
                instruction=f"""Generate implementation focusing on simplicity and directness:
                Problem Classification: {problem_classification}
                
                Guidelines:
                1. Use the most straightforward approach that satisfies all examples
                2. Prioritize readability and clarity
                3. Handle all identified edge cases
                4. Match return types exactly as shown in examples
                5. Use descriptive variable names
                6. Include minimal necessary code - no over-engineering
                7. Follow Python conventions (PEP8)
                
                Output ONLY the function implementation, nothing else.""",
                context=problem_classification
            ),
            self.generate(
                instruction=f"""Generate implementation focusing on robustness and edge cases:
                Problem Classification: {problem_classification}
                
                Guidelines:
                1. Explicitly handle all edge cases identified in analysis
                2. Add defensive checks where appropriate
                3. Consider performance implications
                4. Use clear, explicit logic rather than clever shortcuts
                5. Structure code to make edge case handling obvious
                6. Match return types exactly as shown in examples
                7. Include comments for complex logic if needed
                
                Output ONLY the function implementation, nothing else.""",
                context=problem_classification
            ),
            self.generate(
                instruction=f"""Generate implementation focusing on elegance and Pythonic style:
                Problem Classification: {problem_classification}
                
                Guidelines:
                1. Use Python built-ins and idioms where appropriate
                2. Aim for concise, expressive code
                3. Consider using list comprehensions, generators, or other Python features if they fit naturally
                4. Handle edge cases gracefully
                5. Match return types exactly as shown in examples
                6. Prioritize code that clearly expresses intent
                7. Avoid unnecessary complexity
                
                Output ONLY the function implementation, nothing else.""",
                context=problem_classification
            )
        ]
        
        # Execute parallel solution generation
        simple_solution, robust_solution, elegant_solution = await asyncio.gather(*solution_tasks)
        
        # Phase 4: Ensemble synthesis of solutions
        final_solution = await self.ensemble(
            instruction="""Synthesize the best implementation from the candidates:
            1. Evaluate each solution for correctness, simplicity, and edge case handling
            2. Prefer solutions that exactly match the specification without extras
            3. Ensure return types match examples precisely (int vs float matters)
            4. Choose the most readable and maintainable solution
            5. Incorporate the best elements from each candidate if needed
            6. Remove any unnecessary complexity or defensive programming
            7. Verify that the solution handles all identified edge cases
            8. Ensure the function name matches the ENTRY POINT exactly
            
            Output ONLY the final function implementation, nothing else.""",
            contexts_list=[simple_solution, robust_solution, elegant_solution]
        )
        
        # Phase 5: Iterative refinement with simulated validation
        for iteration in range(2):  # Maximum 2 refinement iterations
            validation_analysis = await self.generate(
                instruction=f"""Critically analyze this implementation for potential issues:
                Implementation: {final_solution}
                
                Check for:
                1. Does it handle all edge cases identified in analysis?
                2. Does it match the examples in the docstring exactly?
                3. Are there any logical errors or off-by-one mistakes?
                4. Is the return type correct for all cases?
                5. Are there any unnecessary imports or complexity?
                6. Does the function name match the ENTRY POINT exactly?
                7. Is the code as simple as possible while being correct?
                
                If issues are found, describe them specifically. If no issues, say "PASSED".
                Be extremely thorough - this code must pass hidden test cases.""",
                context=final_solution
            )
            
            if "PASSED" in validation_analysis.upper() and "ISSUE" not in validation_analysis.upper():
                break  # No issues found, exit loop
            else:
                final_solution = await self.revise(
                    instruction=f"""Revise the implementation to fix the issues identified:
                    Current Implementation: {final_solution}
                    Issues Found: {validation_analysis}
                    
                    Guidelines:
                    1. Fix all identified issues while preserving correct functionality
                    2. Keep the solution as simple as possible
                    3. Maintain exact match with specification
                    4. Don't add unnecessary features or complexity
                    5. Ensure function name matches ENTRY POINT exactly
                    6. Output ONLY the revised function implementation, nothing else.""",
                    context=final_solution
                )
        
        return final_solution