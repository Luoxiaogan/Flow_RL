# Workflow ID: mbppplus_166_0
# Benchmark: mbppplus
# Data Indices: [333, 120]

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

        # Phase 1: Parallel multi-perspective problem classification
        classification_prompts = [
            """Analyze this programming problem from a MATHEMATICAL perspective:
            - Identify if it involves recursion, combinatorics, number theory, or sequences
            - Determine if closed-form, recursive, or iterative solution is optimal
            - Note any mathematical identities or properties that could simplify solution
            - Predict computational complexity concerns""",
            
            """Analyze this programming problem from an ALGORITHMIC perspective:
            - Classify as dynamic programming, greedy, divide-and-conquer, etc.
            - Identify data structures needed (arrays, matrices, trees, graphs)
            - Note traversal patterns (grid, tree, sequence) and state dependencies
            - Highlight any optimization opportunities or bottlenecks""",
            
            """Analyze this programming problem from a STRUCTURAL perspective:
            - Extract exact function signature requirements (names, parameters, return types)
            - Identify explicit and implicit edge cases (empty inputs, boundaries, duplicates)
            - Note any type conversion or consistency requirements
            - List all constraints and invariants that must be preserved"""
        ]
        
        classifications = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in classification_prompts]
        )
        
        # Phase 2: Synthesize unified problem ontology
        problem_ontology = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified problem ontology with this structure:
            PROBLEM TYPE: [recursive/dp/greedy/etc.]
            INPUT CONTRACT: [parameter types, constraints, edge cases]
            OUTPUT CONTRACT: [return type, format, precision requirements]
            SOLUTION STRATEGY: [step-by-step approach with key insights]
            VALIDATION PLAN: [test cases to prioritize, edge cases to generate]
            CONFIDENCE LEVEL: [high/medium/low based on analysis consistency]""",
            contexts_list=classifications
        )

        # Phase 3: Decompose into subproblems
        decomposition = await self.decompose(
            instruction=f"""Break this problem into minimal, testable subproblems based on the ontology:
            {problem_ontology}
            
            For each subproblem:
            - Must be independently solvable
            - Must have clear input/output
            - Must specify dependencies on other subproblems
            - Must include validation criteria
            
            Return as structured list with id, description, dependencies""",
            context=problem_ontology
        )

        # Phase 4: Parallel subproblem solution generation
        subproblem_solutions = {}
        for subproblem in decomposition:
            sub_id = subproblem['id']
            deps = [subproblem_solutions[dep_id] for dep_id in subproblem.get('dependencies', '').split(',') if dep_id in subproblem_solutions]
            context = "\n".join(deps) if deps else ""
            
            solution = await self.generate(
                instruction=f"""Solve this subproblem with extreme precision:
                PROBLEM ONTOLOGY: {problem_ontology}
                SUBPROBLEM: {subproblem['description']}
                DEPENDENCIES: {context}
                
                Requirements:
                - Match exact function signature from original problem
                - Handle all edge cases mentioned in ontology
                - Use appropriate data types and structures
                - Include necessary imports if any
                - Write production-ready, defensive code
                - No explanatory comments - only implementation""",
                context=context
            )
            subproblem_solutions[sub_id] = solution

        # Phase 5: Integrate sub-solutions into complete function
        all_solutions_text = "\n\n".join([f"SUBPROBLEM {k}: {v}" for k, v in subproblem_solutions.items()])
        integrated_solution = await self.revise(
            instruction=f"""Integrate these sub-solutions into a single, coherent function:
            {all_solutions_text}
            
            Integration rules:
            - Preserve exact function name and signature from original problem
            - Resolve any variable naming conflicts
            - Ensure control flow matches problem logic
            - Add any missing edge case handlers
            - Maintain type consistency throughout
            - Include all necessary imports at top
            - Return ONLY the function implementation - no wrappers, no explanations""",
            context=all_solutions_text
        )

        # Phase 6: Basic test validation with revision loop
        final_code = integrated_solution
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # Extract test cases from problem text if available
                test_cases = []
                if "assert" in self.problem_text:
                    test_lines = [line.strip() for line in self.problem_text.split('\n') if "assert" in line]
                    test_cases = [line for line in test_lines if line.startswith("assert")]
                
                if test_cases:
                    test_context = "\n".join(test_cases)
                    validation_result = await self.programmer(
                        instruction=f"""Execute this code against the provided test cases:
                        {test_context}
                        
                        Requirements:
                        - Run exactly as written
                        - Report any failures with specific error messages
                        - If all pass, output 'ALL TESTS PASSED'""",
                        context=final_code,
                        max_retries=1
                    )
                    
                    if "ALL TESTS PASSED" not in validation_result:
                        if attempt < max_retries:
                            final_code = await self.revise(
                                instruction=f"""The code failed validation:
                                {validation_result}
                                
                                Fix ONLY the specific issue causing failure. Preserve all other logic.
                                Consider: edge case handling, type mismatches, off-by-one errors, or base case flaws.
                                Return the complete corrected function.""",
                                context=final_code
                            )
                            continue
                        else:
                            # Final attempt - try more aggressive revision
                            final_code = await self.revise(
                                instruction=f"""The code is still failing validation:
                                {validation_result}
                                
                                Completely rethink the solution approach while preserving function signature.
                                Consider alternative algorithms or data structures.
                                Return the complete revised function.""",
                                context=final_code
                            )
                break
            except Exception as e:
                if attempt < max_retries:
                    final_code = await self.revise(
                        instruction=f"""Code execution failed with error: {str(e)}
                        Diagnose whether this is syntax, logic, or edge case issue.
                        Rewrite only the problematic section while preserving overall structure.
                        Return complete function.""",
                        context=final_code
                    )
                else:
                    break

        # Phase 7: Proactive edge case validation (parallel)
        edge_case_validation = await self.generate(
            instruction=f"""Generate 3 challenging edge cases not shown in the problem:
            PROBLEM ONTOLOGY: {problem_ontology}
            CURRENT SOLUTION: {final_code}
            
            For each edge case:
            - Describe input scenario (empty, boundary, extreme, malformed)
            - Predict expected output with reasoning
            - Write as executable assert statement
            
            Format as Python assert statements only.""",
            context=final_code
        )

        # Execute edge case tests in background (fire and forget for robustness)
        try:
            await self.programmer(
                instruction="Execute these edge case tests against the solution. Report any failures.",
                context=f"{final_code}\n\n{edge_case_validation}",
                max_retries=1
            )
        except:
            # Don't fail workflow on edge case failures - just log internally
            pass

        # Phase 8: Final certification and formatting
        certified_solution = await self.summarize(
            instruction=f"""Produce the final answer with strict formatting:
            - Include ONLY the function implementation
            - Preserve exact function name and signature
            - Include all necessary imports at top of function
            - No wrappers, no explanations, no comments
            - Ensure type consistency and edge case handling
            - Format exactly as required by problem specification
            
            Validate against this checklist:
            [x] Correct function name
            [x] Correct parameter names
            [x] Correct return type
            [x] Handles empty/edge cases
            [x] No external dependencies beyond standard library
            
            FINAL OUTPUT FORMAT: