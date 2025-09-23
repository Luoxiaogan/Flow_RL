# Workflow ID: mbppplus_91_0
# Benchmark: mbppplus
# Data Indices: [189, 127, 93]

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
        import json

        # Phase 1: Parallel multi-perspective problem analysis
        analysis_tasks = [
            self.generate(
                instruction="""Perform deep structural analysis:
                1. Identify the core computational pattern (e.g., mapping, filtering, aggregation, validation)
                2. Determine input/output data types and structures
                3. Extract implicit constraints from test cases
                4. Identify potential edge cases (empty inputs, single elements, boundary values)
                5. Classify problem type: mathematical, logical, structural, or hybrid
                Present as structured JSON with keys: pattern, types, constraints, edge_cases, classification""",
                context=""
            ),
            self.generate(
                instruction="""Perform semantic analysis:
                1. Paraphrase the problem in plain English
                2. Identify key verbs and nouns that define the operation
                3. Map test cases to underlying requirements
                4. Identify any ambiguities or potential misinterpretations
                5. Suggest 2-3 different approaches that could solve this
                Format as markdown with clear section headers""",
                context=""
            ),
            self.generate(
                instruction="""Perform test case reverse engineering:
                1. Analyze provided test cases to infer hidden requirements
                2. Identify what each test case is specifically checking for
                3. Generate 3 additional edge case tests that would validate robustness
                4. Determine expected output format and type from test patterns
                5. Flag any inconsistencies between description and tests
                Return as numbered list with explanations""",
                context=""
            )
        ]
        
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Phase 2: Synthesize comprehensive problem understanding
        problem_understanding = await self.ensemble(
            instruction="""Synthesize all analyses into unified problem specification:
            1. Combine structural, semantic, and test insights
            2. Resolve any contradictions between analyses
            3. Create definitive list of requirements and constraints
            4. Prioritize edge cases that must be handled
            5. Specify exact return type and format requirements
            6. Outline optimal solution strategy
            Output as comprehensive specification document with clear sections""",
            contexts_list=analyses
        )

        # Phase 3: Parallel solution generation
        solution_tasks = [
            self.generate(
                instruction=f"""Generate solution based on structural analysis:
                Problem understanding: {problem_understanding[:2000]}
                Requirements:
                - Implement exact function signature
                - Handle all identified edge cases
                - Match expected return type
                - Optimize for clarity and correctness
                - Include type handling and defensive checks
                Return ONLY the function implementation with imports""",
                context=problem_understanding
            ),
            self.generate(
                instruction=f"""Generate solution from first principles:
                Ignore any reference solutions. Based purely on problem description:
                {self.problem_text[:1000]}
                And test case patterns:
                {analyses[2][:1000]}
                Derive solution from fundamental principles. Consider multiple approaches
                and select most robust. Ensure comprehensive edge case handling.
                Return ONLY the function implementation with imports""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate test-driven solution:
                Focus exclusively on passing all test cases including generated edge cases:
                {analyses[2]}
                Write minimal code that satisfies all tests. Then expand to handle
                general case. Pay special attention to type consistency and boundary
                conditions. Return ONLY the function implementation with imports""",
                context=problem_understanding
            )
        ]
        
        solutions = await asyncio.gather(*solution_tasks)

        # Phase 4: Adversarial validation and refinement loop
        best_solution = solutions[0]
        for iteration in range(3):
            # Generate validation tests
            validation_context = f"Solution: {best_solution}\n\nProblem: {problem_understanding}"
            validation_tests = await self.generate(
                instruction="""Generate 5 adversarial test cases designed to break this solution:
                1. Include edge cases not mentioned in original problem
                2. Test type boundaries and conversions
                3. Include malformed inputs if applicable
                4. Test performance boundaries
                5. Include cases that exploit potential logical flaws
                Format as Python assert statements with explanations""",
                context=validation_context
            )
            
            # Validate solution against adversarial tests
            validation_result = await self.generate(
                instruction=f"""Execute these adversarial tests mentally against the solution:
                Tests: {validation_tests}
                Solution: {best_solution}
                Identify which tests fail and why. If all pass, return 'ALL_TESTS_PASS'.
                If any fail, explain exactly why and what needs to be fixed.
                Be brutally honest - this is adversarial validation.""",
                context=validation_context
            )
            
            if "ALL_TESTS_PASS" in validation_result:
                break
            
            # Revise solution based on failures
            best_solution = await self.revise(
                instruction=f"""Revise solution to fix these failures:
                Validation failures: {validation_result}
                Original requirements: {problem_understanding[:1000]}
                Preserve existing correct behavior while fixing identified issues.
                Strengthen edge case handling and type safety.
                Return ONLY the revised function implementation with imports""",
                context=best_solution
            )

        # Phase 5: Final ensemble with type/format validation
        final_solutions = [best_solution] + solutions[1:]  # Include other candidates
        final_solution = await self.ensemble(
            instruction="""Select and refine final solution:
            1. Evaluate each solution for correctness, robustness, and clarity
            2. Ensure exact function signature match
            3. Verify return type matches requirements
            4. Check for comprehensive edge case handling
            5. Optimize for readability without sacrificing correctness
            6. If solutions have complementary strengths, synthesize them
            Return ONLY the final function implementation with imports""",
            contexts_list=final_solutions
        )

        # Phase 6: Output sanitization and verification
        sanitized_solution = await self.revise(
            instruction="""Final verification and sanitization:
            1. Ensure ONLY function implementation is returned (no explanations)
            2. Verify imports are included and correct
            3. Confirm function name matches exactly
            4. Check parameter names match specification
            5. Ensure return type consistency
            6. Remove any debug code or comments
            Return ONLY the clean function implementation with imports""",
            context=final_solution
        )

        return sanitized_solution