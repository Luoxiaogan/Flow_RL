# Workflow ID: mbppplus_48_0
# Benchmark: mbppplus
# Data Indices: [92, 293]

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
        Universal workflow for programming problem domain.
        Dynamically infers problem type, generates multiple solutions, validates, and refines.
        """
        import asyncio
        import re

        # Phase 1: Problem Deconstruction — Understand the task, types, edge cases
        deconstruction = await self.generate(
            instruction="""Thoroughly analyze the programming task. Extract:
            1. Input type (e.g., string, list, number)
            2. Expected output type (e.g., tuple, string, list)
            3. Core transformation (e.g., "remove extra spaces", "parse floats from comma-separated string")
            4. Key edge cases (e.g., empty input, single element, malformed data, whitespace-only)
            5. Any implicit constraints (e.g., preserve order, no external libraries unless necessary)
            Format as a structured dictionary with keys: 'input_type', 'output_type', 'transformation', 'edge_cases', 'constraints'.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation — Try multiple implementation strategies
        solution_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Implement the function based on this analysis:
                {deconstruction}
                
                Strategy 1: Use built-in string methods and simple splits. Avoid regex unless necessary.
                Handle all edge cases mentioned. Return correct type. No extra prints or explanations.
                Generate ONLY the function code with necessary imports inside the function if needed.""",
                context=deconstruction
            ),
            self.programmer(
                instruction=f"""Implement the function based on this analysis:
                {deconstruction}
                
                Strategy 2: Use regular expressions or advanced parsing if applicable.
                Prioritize robustness and edge case handling. Return correct type.
                Generate ONLY the function code with necessary imports inside the function if needed.""",
                context=deconstruction
            ),
            self.programmer(
                instruction=f"""Implement the function based on this analysis:
                {deconstruction}
                
                Strategy 3: Use functional programming (map, filter, comprehensions) for transformations.
                Ensure type safety and edge case coverage. Return correct type.
                Generate ONLY the function code with necessary imports inside the function if needed.""",
                context=deconstruction
            )
        )

        # Phase 3: Ensemble Selection — Evaluate and pick the best or synthesize
        selected_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions. Criteria:
            1. Correctness: Does it match the transformation? Handle edge cases?
            2. Type Safety: Does it return the exact expected type?
            3. Simplicity: Is it readable and not over-engineered?
            4. Robustness: Does it fail gracefully or handle malformed input?
            Select the single best solution. If multiple are equally good, pick the simplest.
            Return ONLY the raw function code — no markdown, no explanations, no extra text.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Validation & Refinement — Fix any remaining issues
        final_solution = await self.revise(
            instruction="""Review this code for:
            - Missing edge case handling (especially empty input, single element, malformed data)
            - Type mismatches (e.g., returning list instead of tuple)
            - Unnecessary complexity or imports
            - Syntax errors or logical flaws
            If any issues, fix them. Otherwise, return the code unchanged.
            Output ONLY the final function implementation — nothing else.""",
            context=selected_solution
        )

        return final_solution