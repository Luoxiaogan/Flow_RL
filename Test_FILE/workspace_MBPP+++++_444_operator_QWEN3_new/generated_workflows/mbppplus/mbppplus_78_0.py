# Workflow ID: mbppplus_78_0
# Benchmark: mbppplus
# Data Indices: [249, 216, 268]

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

        # Phase 1: Parallel problem classification and constraint extraction
        classification_task = self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary category: list/tuple, string, math, data structure, or logic
            2. Extract explicit constraints: input types, output format, edge conditions
            3. Infer implicit constraints: mathematical properties, logical invariants, boundary behaviors
            4. Predict failure modes: what edge cases might break naive solutions?
            5. Hypothesize solution strategy: filtering, transformation, validation, recursion?
            Format as structured JSON with keys: category, constraints, failure_modes, strategy""",
            context=""
        )
        
        sample_analysis_task = self.generate(
            instruction="""Analyze provided test cases:
            1. Extract input-output patterns
            2. Identify type signatures (list vs tuple vs set, int vs float)
            3. Detect hidden constraints (order preservation, uniqueness, mutability)
            4. Reverse-engineer validation criteria from assertions
            Return as bullet-point analysis""",
            context=""
        )

        # Execute classification and sample analysis in parallel
        classification, sample_analysis = await asyncio.gather(classification_task, sample_analysis_task)

        # Phase 2: Generate multiple solution perspectives
        solution_perspectives = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution from mathematical perspective:
                Problem classification: {classification}
                Test case patterns: {sample_analysis}
                Requirements:
                - Handle all edge cases mentioned in classification
                - Match exact return type from test cases
                - Include defensive checks for invalid inputs
                - Use efficient algorithms where applicable
                - Add inline comments for complex logic
                Return ONLY the function implementation with imports""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution from defensive programming perspective:
                Focus on:
                - Input validation and type checking
                - Graceful handling of edge cases (empty, null, boundary)
                - Explicit error conditions with clear return values
                - Code readability and maintainability
                Problem context: {classification}
                Test patterns: {sample_analysis}
                Return ONLY the function implementation with imports""",
                context=""
            )
        )

        # Phase 3: Adversarial validation ensemble
        validation_tasks = []
        for i, solution in enumerate(solution_perspectives):
            validation_tasks.append(
                self.generate(
                    instruction=f"""Critique solution {i+1}:
                    1. Does it handle ALL edge cases from classification: {classification}?
                    2. Does return type match test case expectations: {sample_analysis}?
                    3. Are there off-by-one errors or boundary condition flaws?
                    4. Is logic sound for extreme values (empty, single element, duplicates)?
                    5. Generate 3 additional test cases not in original problem
                    Return structured critique with 'issues' list and 'suggested_fixes'""",
                    context=solution
                )
            )
        
        # Run validations in parallel
        validations = await asyncio.gather(*validation_tasks)

        # Phase 4: Ensemble best solution with revision
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Completeness of edge case handling
            2. Alignment with test case patterns
            3. Code clarity and maintainability
            4. Efficiency and elegance
            If both have significant flaws, synthesize a hybrid solution""",
            contexts_list=solution_perspectives
        )

        # Phase 5: Iterative refinement loop (max 2 iterations)
        current_solution = selected_solution
        for iteration in range(2):
            # Summarize current state to avoid context bloat
            summary = await self.summarize(
                instruction="Condense current solution and validation feedback into 3 key improvement points",
                context=f"Solution: {current_solution}\nValidations: {'; '.join(validations)}"
            )
            
            # Generate refined solution
            refined_solution = await self.generate(
                instruction=f"""Revise solution based on feedback:
                Key improvement points: {summary}
                Original classification: {classification}
                Test case patterns: {sample_analysis}
                Requirements:
                - Fix all identified issues
                - Maintain correct function signature
                - Preserve type consistency
                - Add comments for complex edge case handling
                Return ONLY the function implementation with imports""",
                context=current_solution
            )
            
            # Validate refined solution
            refinement_validation = await self.generate(
                instruction=f"""Final validation:
                1. Verify all previous issues are resolved
                2. Check against original test cases
                3. Validate with generated edge cases
                4. Confirm no new issues introduced
                Return 'PASSED' if fully correct, otherwise detailed issues""",
                context=refined_solution
            )
            
            if "PASSED" in refinement_validation.upper():
                return refined_solution
            else:
                current_solution = refined_solution
                # Update validations for next iteration
                validations = [refinement_validation]

        # Return best available solution after iterations
        return current_solution