# Workflow ID: mbppplus_39_0
# Benchmark: mbppplus
# Data Indices: [303, 344, 104]

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
        Uses multi-perspective generation, adversarial validation, and adaptive synthesis.
        """
        import asyncio
        import re

        # PHASE 1: Problem Decomposition & Contract Extraction
        contract_analysis = await self.generate(
            instruction="""Thoroughly analyze the problem to extract its implicit contract:
            1. Identify the exact function signature (name, parameters) from the reference.
            2. Infer input types and output types from test cases and description.
            3. List all edge cases mentioned or implied (empty inputs, negatives, floats, duplicates, etc.).
            4. Determine if order matters, if duplicates are allowed, if type coercion is needed.
            5. Extract any mathematical, logical, or structural constraints.
            Format as structured JSON-like text with sections: signature, types, edge_cases, constraints.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (3 Perspectives)
        solution_tasks = [
            self.generate(
                instruction=f"""Generate a solution from a MATHEMATICAL/LOGICAL perspective:
                - Focus on formal definitions (e.g., evenness = divisible by 2 with no remainder).
                - Handle edge cases mathematically (negative numbers, zero, floats).
                - Ensure type correctness based on contract: {contract_analysis}
                - Return code ONLY — no explanations. Match function signature exactly.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution from a STRUCTURAL/DATA-TYPE perspective:
                - Focus on data structure transformations (list→set, tuple→list, etc.).
                - Preserve or discard order as required by contract: {contract_analysis}
                - Handle nesting, mutability, and type conversions explicitly.
                - Return code ONLY — no explanations. Match function signature exactly.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution from an EDGE-CASE/ADVERSARIAL perspective:
                - Assume the problem is designed to trick you. Hunt for loopholes.
                - Test boundaries: None, NaN, inf, empty collections, single elements, duplicates.
                - Add defensive checks if contract implies strictness: {contract_analysis}
                - Return code ONLY — no explanations. Match function signature exactly.""",
                context=""
            )
        ]
        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 3: Parallel Adversarial Validation
        validation_tasks = [
            self.revise(
                instruction=f"""CRITIQUE this solution adversarially:
                - Does it handle ALL edge cases from contract: {contract_analysis}?
                - Does return type EXACTLY match test case outputs (set vs list vs tuple)?
                - Will it fail on type mismatches, overflow, or silent conversions?
                - Inject 3 malicious test cases it might fail on.
                - If flawed, rewrite to fix — otherwise return unchanged.
                - Preserve function signature exactly.""",
                context=sol
            ) for sol in raw_solutions
        ]
        validated_solutions = await asyncio.gather(*validation_tasks)

        # PHASE 4: Adaptive Synthesis via Ensemble
        final_code = await self.ensemble(
            instruction=f"""Synthesize a FINAL SOLUTION from these candidates:
            Contract: {contract_analysis}
            Candidates: {validated_solutions}

            RULES:
            1. Prefer solutions that explicitly handle edge cases mentioned in contract.
            2. Enforce exact return type matching test case patterns (e.g., if tests show sets, return set).
            3. Resolve conflicts by deferring to mathematical correctness + test case evidence.
            4. Merge robustness: if one solution handles floats and another handles negatives, combine.
            5. Output ONLY the function code — no markdown, no explanations. Include necessary imports inside function if needed.
            6. Preserve original function name and parameter names exactly.""",
            contexts_list=validated_solutions
        )

        # PHASE 5: Final Sanitization (Remove any markdown/code block wrappers)
        clean_code = re.sub(r'