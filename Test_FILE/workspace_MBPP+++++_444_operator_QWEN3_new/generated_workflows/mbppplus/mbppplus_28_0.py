# Workflow ID: mbppplus_28_0
# Benchmark: mbppplus
# Data Indices: [42, 47, 191]

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
        Universal workflow for programming problem-solving domain.
        Adapts strategy based on problem classification, validates against edge cases,
        and ensures strict compliance with signature and return type requirements.
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL PROBLEM ANALYSIS (Diamond Fork)
        # Generate multiple analytical perspectives simultaneously
        analysis_tasks = [
            self.generate(
                instruction="""Perform deep structural analysis of the programming problem:
                1. Identify the primary data type involved (string, list, tuple, number, etc.)
                2. Determine the core operation (search, transform, count, validate, etc.)
                3. Extract any explicit patterns, constraints, or boundary conditions
                4. Infer likely edge cases (empty inputs, single elements, duplicates, type boundaries)
                5. Classify problem category from: regex, list_ops, math, string_manip, data_struct, logic
                Present as structured JSON with keys: dataType, operation, constraints, edgeCases, category""",
                context=""
            ),
            self.generate(
                instruction="""Extract all functional requirements from the problem:
                1. What is the exact input format? (include type and structure)
                2. What is the required output format? (include type and structure)
                3. Are there any explicit examples or test cases shown?
                4. What constitutes success? (exact match, approximate, boolean, etc.)
                5. Are there performance or efficiency constraints implied?
                Format as bullet points with clear labels""",
                context=""
            ),
            self.generate(
                instruction="""Propose 3 distinct solution strategies:
                Strategy 1: Most straightforward/naive approach
                Strategy 2: Most efficient/optimized approach
                Strategy 3: Most robust/defensive approach (handles edge cases explicitly)
                For each, outline: key steps, required libraries, potential pitfalls, and edge case handling.
                Prioritize strategies that match the problem's apparent complexity level.""",
                context=""
            )
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # PHASE 2: SYNTHESIZE ANALYSIS & SELECT STRATEGY (Diamond Merge)
        synthesis = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem understanding and select the optimal solution strategy:
            1. Consolidate data type, operation, and constraints from Analysis 1
            2. Cross-validate with requirements from Analysis 2
            3. Evaluate proposed strategies from Analysis 3 against consolidated requirements
            4. Select ONE strategy that best balances: correctness, simplicity, and edge case coverage
            5. Justify selection with specific references to problem constraints
            Output format: 
            - Problem Summary: [concise description]
            - Selected Strategy: [number and name]
            - Key Implementation Notes: [critical considerations for coding]
            - Required Imports: [list of modules needed]""",
            contexts_list=analysis_results
        )

        # PHASE 3: GENERATE INITIAL SOLUTION
        initial_solution = await self.generate(
            instruction=f"""Generate a complete Python function implementation based on this synthesis:
            {synthesis}
            
            STRICT REQUIREMENTS:
            - Use EXACT function name and parameters from problem
            - Include ALL necessary imports at top of function (inside run_workflow)
            - Return EXACT data type specified (list vs tuple vs string matters)
            - Handle ALL inferred edge cases from analysis
            - Code must be self-contained (no external dependencies beyond stdlib)
            - Include minimal comments only if critical for clarity
            
            Format output as raw Python code block with no additional text.""",
            context=synthesis
        )

        # PHASE 4: VALIDATE & REVISE (Cascade with Feedback)
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Critically validate this solution against problem requirements:
                {synthesis}
                
                CHECKLIST:
                1. Does function signature exactly match? (name, params)
                2. Are all required imports included?
                3. Does return type match expected type?
                4. Are edge cases handled? (test with: empty input, single element, max/min values)
                5. Is logic correct for sample cases shown?
                6. Any off-by-one errors or index issues?
                7. Any type conversion issues? (str/int/list mismatches)
                
                If any issues found, describe them SPECIFICALLY with line numbers if possible.
                If perfect, respond only with 'VALIDATED'.""",
                context=initial_solution
            )
            
            if "VALIDATED" in validation:
                break
                
            # Revise based on validation feedback
            initial_solution = await self.revise(
                instruction=f"""Revise the solution to fix these specific issues:
                {validation}
                
                PRESERVE:
                - Original function signature
                - Core algorithmic approach (unless fundamentally flawed)
                - Required imports
                
                IMPROVE:
                - Fix all identified bugs
                - Add edge case handling where missing
                - Ensure type consistency
                - Maintain clean, readable code
                
                Return ONLY the revised Python code block.""",
                context=initial_solution
            )
        else:
            # If we exhausted iterations, do one final ensemble with original
            initial_solution = await self.ensemble(
                instruction="""Select the most robust version between original and revised solutions.
                Prioritize: correctness > edge case handling > simplicity.
                If both flawed, synthesize a new version combining their strengths.
                Return ONLY the final Python code block.""",
                contexts_list=[analysis_results[0], initial_solution]
            )

        # PHASE 5: FINAL COMPLIANCE CHECK & CLEANUP
        final_code = await self.revise(
            instruction="""Perform final compliance check:
            1. Ensure code is ONLY the function implementation (no extra text)
            2. Verify imports are inside run_workflow (not at top of file)
            3. Confirm function name and parameters match exactly
            4. Remove any debug prints or unnecessary comments
            5. Ensure proper indentation and Python syntax
            
            Return ONLY the cleaned Python code block ready for execution.""",
            context=initial_solution
        )

        return final_code