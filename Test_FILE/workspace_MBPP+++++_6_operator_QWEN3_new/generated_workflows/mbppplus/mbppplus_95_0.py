# Workflow ID: mbppplus_95_0
# Benchmark: mbppplus
# Data Indices: [50, 154]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem-solving domain.
        Dynamically infers problem type, decomposes into subtasks,
        generates robust code with edge case handling, and delivers
        clean function implementation.
        """
        import asyncio
        import re

        # Phase 1: Parallel Problem Interpretation
        # Generate multiple analytical perspectives to infer intent
        interpretations = await asyncio.gather(
            self.generate(
                instruction="""Analyze the function signature and problem context to infer:
                - Primary operation (e.g., set membership, sorting, filtering, transformation)
                - Expected input/output types and constraints
                - Likely edge cases (empty inputs, duplicates, single elements, type boundaries)
                - Common programming conventions implied by function name
                - Return type requirements (must match signature exactly)
                Provide structured analysis with clear categorization.""",
                context=""
            ),
            self.generate(
                instruction="""Focus on edge case identification:
                - What are the minimum valid inputs?
                - What constitutes invalid or boundary inputs?
                - How should duplicates be handled?
                - What return values are expected for edge cases (None, empty, error)?
                - Are there implicit type conversion requirements?
                List all potential edge scenarios with handling strategies.""",
                context=""
            ),
            self.generate(
                instruction="""Derive algorithmic approach:
                - What core operations are needed (set, sort, filter, map, reduce)?
                - What data structure transformations are implied?
                - What is the optimal order of operations?
                - Are there efficiency constraints or preferences?
                - How to preserve type consistency throughout?
                Outline step-by-step algorithm with justifications.""",
                context=""
            )
        )

        # Phase 2: Synthesize Unified Specification
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent problem specification:
            - Combine intent, edge cases, and algorithm into unified plan
            - Resolve any contradictions between analyses
            - Prioritize robustness and type safety
            - Ensure all edge cases are explicitly addressed
            - Format as clear, actionable development specification""",
            contexts_list=interpretations
        )

        # Phase 3: Decompose into Subproblems
        subproblems = await self.decompose(
            instruction="""Break the unified specification into atomic, independent subproblems:
            - Each subproblem should be solvable with a single code snippet
            - Include: input validation, data transformation, core operation, edge handling, type conversion
            - Specify dependencies between subproblems
            - Ensure coverage of all edge cases identified
            - Output as structured list with clear descriptions""",
            context=unified_spec
        )

        # Phase 4: Summarize for Context Efficiency
        summarized_plan = await self.summarize(
            instruction="""Condense the decomposition into a concise execution plan:
            - Preserve all critical steps and edge case handlers
            - Remove redundant explanations
            - Format as bullet-point checklist for code generation
            - Include type requirements and return specifications""",
            context=str(subproblems)
        )

        # Phase 5: Generate Initial Implementation
        initial_code = await self.programmer(
            instruction=f"""Generate Python function implementation based on this plan:
            {summarized_plan}
            
            STRICT REQUIREMENTS:
            - Match function signature EXACTLY (name, parameters)
            - Handle ALL identified edge cases
            - Return correct data type (tuple, list, scalar, None as appropriate)
            - Include necessary imports INSIDE function if needed
            - NO wrapper functions, NO extra text, NO markdown
            - Output ONLY the raw function implementation as string
            - Ensure code is efficient and readable""",
            context=summarized_plan,
            max_retries=1
        )

        # Phase 6: Iterative Hardening Against Edge Cases
        current_code = initial_code
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Critically evaluate this code for edge case robustness:
                {current_code}
                
                Check for:
                - Empty input handling
                - Single element cases
                - All-duplicate scenarios
                - Type preservation
                - Boundary value correctness
                - Return type compliance
                - Potential exceptions or crashes
                List specific issues found, or say 'PASSED' if flawless.""",
                context=current_code
            )
            
            if "PASSED" in validation.upper() and "ISSUE" not in validation.upper():
                break
                
            # Revise based on validation feedback
            current_code = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                Validation feedback: {validation}
                
                Requirements:
                - Preserve original function signature
                - Maintain all existing functionality
                - Add missing edge case handlers
                - Ensure type safety
                - Output ONLY the raw function implementation
                - No explanations, no markdown, no extra text""",
                context=current_code
            )

        # Phase 7: Final Sanitization and Delivery
        # Ensure output is clean function implementation only
        final_code = await self.revise(
            instruction="""Sanitize this code for final delivery:
            - Remove any explanatory comments or markdown
            - Ensure ONLY function implementation remains
            - Verify imports are inside function if needed
            - Confirm exact signature match
            - Strip all extra whitespace or formatting
            - Output raw code string with nothing else""",
            context=current_code
        )

        return final_code