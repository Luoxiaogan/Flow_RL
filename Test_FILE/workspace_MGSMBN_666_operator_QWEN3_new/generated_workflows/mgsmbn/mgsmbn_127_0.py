# Workflow ID: mgsmbn_127_0
# Benchmark: mgsmbn
# Data Indices: [144]

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
        Universal workflow for solving MGSM Bengali math word problems.
        Architecture: Semantic Extraction → Hierarchical Decomposition → Parallel Computation → Validation → Answer Extraction
        """
        import asyncio
        import re

        # PHASE 1: SEMANTIC EXTRACTION — Extract all entities, numbers, operations, and relationships
        semantic_map = await self.generate(
            instruction="""You are a semantic extractor for Bengali math word problems. Your task:
            1. Identify every numerical value (integers, decimals, fractions, percentages) and what it represents.
            2. Identify every named entity (people, organizations, objects) and their roles.
            3. Identify every mathematical operation or relationship (spend, donate, remain, total, half, etc.) with explicit dependencies.
            4. Identify units (টাকা, ডলার, ঘণ্টা, etc.) and normalize if mixed (assume USD if unspecified).
            5. Identify the final question — what is being asked for?
            6. Flag any ambiguities or missing information.
            Format output as a structured list with clear labels. Do not solve — only extract and structure.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION — Break into ordered, dependent calculation steps
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, atomic calculation steps that must be executed in sequence.
            Rules:
            - Each step must compute exactly one value.
            - Each step must depend only on previously computed values or given constants.
            - Represent fractions, percentages, and remainders as explicit operations.
            - If solving for an unknown, represent it as 'x' and derive the equation.
            - Include the formula or operation in plain text for each step.
            - Steps must follow chronological or logical order as implied by the problem.
            - Do not skip intermediate steps — even if trivial.
            Output as list of subproblems with 'id', 'description', and 'dependencies'.""",
            context=semantic_map
        )

        # PHASE 3: REVISE DECOMPOSITION — Validate logic and fix misinterpretations
        revised_decomposition = await self.revise(
            instruction=f"""Critically review the decomposition:
            - Verify that 'অবশিষ্ট' (remainder) always refers to amount after prior subtractions.
            - Ensure fractions/percentages are applied to correct base values.
            - Check that dependencies are correctly ordered.
            - Confirm that the final step computes the value asked in the question.
            - If any step is ambiguous or incorrect, rewrite it with corrected logic.
            - Preserve the structured format (id, description, dependencies).
            Original decomposition:
            {decomposition}""",
            context=str(decomposition)
        )

        # PHASE 4: GENERATE EXECUTABLE CODE — Two parallel implementations for robustness
        code_tasks = []
        for strategy in ["Use exact fractions and avoid floating point until final step.", 
                        "Use decimal arithmetic with 4 decimal precision throughout."]:
            code_task = self.generate(
                instruction=f"""Convert the revised decomposition into executable Python code.
                Rules:
                - Assign each step to a variable (step1, step2, ...).
                - Use only basic arithmetic operations (+, -, *, /).
                - Final answer must be stored in variable 'final_answer'.
                - Do not print anything except the final_answer.
                - Assume all currency is in USD unless specified otherwise.
                - If solving for x, use algebraic rearrangement.
                - {strategy}
                Decomposition to follow:
                {revised_decomposition}""",
                context=revised_decomposition
            )
            code_tasks.append(code_task)
        
        code_versions = await asyncio.gather(*code_tasks)

        # PHASE 5: EXECUTE CODE IN PARALLEL
        execution_tasks = [self.programmer(
            instruction="Execute this code and return only the numerical result of 'final_answer'.",
            context=code
        ) for code in code_versions]
        
        execution_results = await asyncio.gather(*execution_tasks)

        # PHASE 6: ENSEMBLE — Resolve discrepancies or select most consistent result
        final_result = await self.ensemble(
            instruction="""You are given multiple numerical results from parallel computations of the same problem.
            - If all results are identical, return that value.
            - If results differ, select the one most consistent with the problem's context (e.g., currency should have 2 decimals, people should be integer).
            - If still ambiguous, prefer the result from the fraction-based computation for exactness.
            - Return ONLY the final numerical value — no explanation, no units.""",
            contexts_list=execution_results
        )

        # PHASE 7: FINAL SANITIZATION — Extract and format the answer
        sanitized_answer = await self.summarize(
            instruction="""Extract the final numerical answer from the text below.
            - If it's a decimal representing currency, round to 2 decimal places.
            - If it represents count of people or objects, round to nearest integer.
            - Remove any non-numeric characters.
            - Return ONLY the number — nothing else.""",
            context=final_result
        )

        # Clean output (remove any residual text, keep only number)
        # Use regex to extract number (handles integers, decimals, negative)
        match = re.search(r'-?\d+\.?\d*', sanitized_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return sanitized_answer.strip()