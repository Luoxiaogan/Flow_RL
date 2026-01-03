# Workflow ID: mbppplus_36_0
# Benchmark: mbppplus
# Data Indices: [81, 89, 161]

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

        # Phase 1: Problem Discovery & Specification Extraction
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Identify the exact transformation or validation being requested
            2. Extract input/output type signatures (list, tuple, int, bool, etc.)
            3. Infer edge cases from examples (empty inputs, single elements, negatives, etc.)
            4. Determine if order preservation, deduplication, or mutability matters
            5. Classify problem type: element-wise ops, consecutive ops, validation, etc.
            6. List all implicit constraints (e.g., "return list not tuple", "no imports allowed")
            Output as structured markdown with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation using imperative style:
                Problem Analysis: {problem_analysis}
                Requirements:
                - Match exact function signature from problem
                - Handle all inferred edge cases
                - Include type guards and input validation
                - Return correct data type (list/tuple/set/bool)
                - Prioritize readability over cleverness
                Output ONLY the function code with necessary imports inside function body if any.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using functional style:
                Problem Analysis: {problem_analysis}
                Requirements:
                - Use map/filter/lambda where appropriate
                - Handle edge cases explicitly
                - Preserve type contracts
                - Include docstring describing behavior
                Output ONLY the function code with necessary imports inside function body if any.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using comprehension style:
                Problem Analysis: {problem_analysis}
                Requirements:
                - Use list/dict/set comprehensions if applicable
                - Handle boundary conditions
                - Match expected return type exactly
                - Include inline comments for complex logic
                Output ONLY the function code with necessary imports inside function body if any.""",
                context=""
            )
        )

        # Phase 3: Adversarial Validation
        validation_tasks = []
        for i, candidate in enumerate(solution_candidates):
            validation_tasks.append(
                self.generate(
                    instruction=f"""Act as adversarial code reviewer for candidate {i+1}:
                    Candidate Code:
                    {candidate}
                    
                    Problem Analysis:
                    {problem_analysis}
                    
                    Tasks:
                    1. Identify all potential failure modes (edge cases, type errors, logic flaws)
                    2. Generate 3-5 unit test assertions that would break this implementation
                    3. Suggest specific fixes for each vulnerability
                    4. Rate robustness on scale 1-10
                    Output as structured report with "VULNERABILITIES", "TEST_CASES", "FIXES", "RATING" sections.""",
                    context=candidate
                )
            )
        
        validation_reports = await asyncio.gather(*validation_tasks)

        # Phase 4: Targeted Revision
        revised_candidates = []
        for i, (candidate, report) in enumerate(zip(solution_candidates, validation_reports)):
            revised = await self.revise(
                instruction=f"""Revise this code using validation feedback:
                Original Code:
                {candidate}
                
                Validation Report:
                {report}
                
                Revision Requirements:
                1. Fix all identified vulnerabilities
                2. Add explicit edge case handling
                3. Ensure type consistency with problem requirements
                4. Maintain original algorithmic approach unless fundamentally flawed
                5. Keep code as concise as possible while being robust
                Output ONLY the revised function code with necessary imports inside function body if any.""",
                context=candidate
            )
            revised_candidates.append(revised)

        # Phase 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best implementation from all revised candidates:
            Evaluation Criteria:
            1. Correctness: Must handle all edge cases from validation reports
            2. Robustness: Highest failure mode coverage
            3. Efficiency: Optimal time/space complexity
            4. Readability: Clear, maintainable code
            5. Type Fidelity: Matches expected input/output types exactly
            
            Synthesis Strategy:
            - Borrow input validation from most defensive candidate
            - Use core logic from most efficient candidate
            - Adopt error handling from highest-rated candidate
            - Ensure final code passes all adversarial test cases
            Output ONLY the final function implementation with necessary imports inside function body if any.""",
            contexts_list=revised_candidates
        )

        # Phase 6: Final Sanitization (remove markdown, extra text)
        clean_solution = await self.revise(
            instruction="""Extract ONLY the Python function code from this text:
            - Remove any markdown, comments, or explanatory text
            - Preserve all imports inside function if present
            - Ensure exact function signature matches problem
            - Output must be ready-to-execute Python code with no wrapping""",
            context=final_solution
        )

        return clean_solution