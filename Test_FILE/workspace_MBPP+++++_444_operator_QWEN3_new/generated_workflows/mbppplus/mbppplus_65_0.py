# Workflow ID: mbppplus_65_0
# Benchmark: mbppplus
# Data Indices: [302, 371, 24]

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

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Thoroughly analyze the problem to determine:
            1. Primary category: Is this a bit manipulation, data structure operation, mathematical computation, or string/list transformation?
            2. Complexity level: Simple (direct operation), Medium (requires loops/conditions), Complex (nested logic or edge-heavy)
            3. Key constraints: What are the input types? Expected return types? Any mentioned edge cases?
            4. Signature requirements: Must preserve exact function name and parameter structure.
            5. Hidden test inference: What edge cases are likely? (e.g., empty inputs, single elements, duplicates, zeros, negatives)
            Output a structured analysis with clear labels for each section.""",
            context=""
        )

        # Step 2: Parallel solution generation along three strategic tracks
        algorithmic_track = asyncio.create_task(self.generate(
            instruction=f"""Generate a solution assuming this is an algorithmic/logical problem.
            Focus on: loop structures, conditionals, step-by-step transformations.
            Explicitly handle edge cases inferred from classification: {classification}
            Ensure return type matches exactly what's implied by examples.
            Include detailed comments explaining logic for maintainability.
            If bit manipulation is involved, consider binary representations or modulus/division approaches.
            Return ONLY the function implementation with necessary imports, nothing else.""",
            context=classification
        ))

        structural_track = asyncio.create_task(self.generate(
            instruction=f"""Generate a solution assuming this is a structural/data-type problem.
            Focus on: built-in operations (like + for tuples), slicing, indexing, type conversions.
            Leverage Python's native capabilities for efficiency.
            Handle edge cases: empty structures, single elements, type mismatches.
            Preserve order if implied by examples.
            Return ONLY the function implementation with necessary imports, nothing else.""",
            context=classification
        ))

        mathematical_track = asyncio.create_task(self.generate(
            instruction=f"""Generate a solution assuming this is a mathematical/computational problem.
            Focus on: arithmetic operations, sequences, number theory, accumulators.
            Consider mathematical optimizations or formula-based approaches.
            Handle edge cases: zero, negative numbers, overflow boundaries.
            Ensure numerical precision and correct data types.
            Return ONLY the function implementation with necessary imports, nothing else.""",
            context=classification
        ))

        # Gather all candidate solutions
        candidates = await asyncio.gather(algorithmic_track, structural_track, mathematical_track)

        # Step 3: Ensemble synthesis with validation focus
        synthesized_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution from the candidates below.
            CRITICAL CRITERIA:
            - Must exactly match function signature (name, parameters)
            - Must handle inferred edge cases (empty, single, boundary values)
            - Must return correct data type (list vs tuple vs int)
            - Must be efficient and readable
            - Must not assume input validation — be defensive
            If candidates conflict, prioritize correctness over cleverness.
            If synthesis is needed, merge the most robust parts of each.
            Output ONLY the final function implementation with imports, nothing else.""",
            contexts_list=candidates
        )

        # Step 4: Iterative validation and revision (up to 3 rounds)
        current_solution = synthesized_solution
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this solution:
                1. Does it handle all inferred edge cases from classification: {classification}?
                2. Does it match the exact return type and structure shown in examples?
                3. Are there any logical flaws, off-by-one errors, or type mismatches?
                4. Is the code efficient and free of unnecessary complexity?
                5. Does it strictly follow the required output format (ONLY function + imports)?
                If no issues, respond 'VALID'. Otherwise, list specific, actionable fixes.""",
                context=current_solution
            )

            if "VALID" in validation_feedback.upper() and len(validation_feedback) < 20:
                break  # Exit early if validated

            # Revise based on feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix these specific issues:
                {validation_feedback}
                
                ALSO ensure:
                - Function signature is preserved exactly
                - Return type matches examples
                - Edge cases from classification are handled: {classification}
                - Code is clean, efficient, and well-commented
                - Output format is STRICT: only function implementation with necessary imports
                
                Return ONLY the revised function code, nothing else.""",
                context=current_solution
            )

        # Final output
        return current_solution