# Workflow ID: mbppplus_34_0
# Benchmark: mbppplus
# Data Indices: [178, 296, 261]

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
        Dynamically adapts to problem type, generates multiple strategies,
        hardens against edge cases, and synthesizes optimal solution.
        """
        import asyncio
        import re

        # Stage 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it by:
            1. Primary operation type (e.g., counting, searching, transforming, filtering, aggregating)
            2. Input data structures (list, string, tuple, mixed, etc.)
            3. Output requirements (dictionary, boolean, list of tuples, etc.)
            4. Critical edge cases (empty inputs, single elements, duplicates, type boundaries)
            5. Implied constraints (order preservation, immutability, performance hints)
            6. Expected Python idioms or standard library modules likely needed
            Format as structured bullet points with clear headers.""",
            context=""
        )

        # Stage 2: Generate edge cases to handle proactively
        edge_cases = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Generate a comprehensive list of edge cases and boundary conditions this solution MUST handle.
            Include at least: empty inputs, single-element inputs, duplicate handling, type edge cases, 
            and any domain-specific boundary conditions mentioned or implied.
            Format as a numbered list with brief explanations.""",
            context=classification
        )

        # Stage 3: Parallel generation of distinct solution strategies
        strategy_instructions = [
            f"""Generate a Python solution focusing on MAXIMUM CORRECTNESS and edge-case robustness.
            Classification context: {classification}
            Must handle these edge cases: {edge_cases}
            Prioritize explicit condition handling over clever one-liners.
            Return ONLY the function implementation with necessary imports inside the function body if needed.
            No explanations, no markdown, no extra text.""",
            
            f"""Generate a Python solution focusing on PYTHONIC EFFICIENCY and standard library usage.
            Classification context: {classification}
            Must handle these edge cases: {edge_cases}
            Use appropriate built-ins (Counter, set, etc.) where applicable.
            Return ONLY the function implementation with necessary imports inside the function body if needed.
            No explanations, no markdown, no extra text.""",
            
            f"""Generate a Python solution focusing on READABILITY and educational clarity.
            Classification context: {classification}
            Must handle these edge cases: {edge_cases}
            Use clear variable names and explicit logic flow.
            Return ONLY the function implementation with necessary imports inside the function body if needed.
            No explanations, no markdown, no extra text."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # Stage 4: Harden each strategy against edge cases
        hardened_strategies = []
        for i, strategy in enumerate(strategies):
            hardened = await self.revise(
                instruction=f"""Revise this solution to explicitly handle ALL these edge cases:
                {edge_cases}
                
                Ensure:
                - No unhandled exceptions for edge inputs
                - Correct return types in all cases
                - Type conversions are explicit and correct (e.g., list to tuple when needed)
                - Imports are included if necessary
                Return ONLY the revised function implementation, nothing else.""",
                context=strategy
            )
            hardened_strategies.append(hardened)

        # Stage 5: Ensemble - Synthesize best solution
        final_solution = await self.ensemble(
            instruction=f"""Select or synthesize the optimal solution from these candidates:
            Consider:
            1. Correctness across all edge cases
            2. Adherence to expected return types and function signatures
            3. Efficiency and Pythonic quality
            4. Robustness and maintainability
            
            If one solution is clearly superior, select it. Otherwise, intelligently merge the best elements.
            CRITICAL: Return ONLY the function implementation code. No explanations, no markdown, no extra text.
            Ensure all necessary imports are included within the function if needed.
            Match the exact function name and signature from the problem specification.""",
            contexts_list=hardened_strategies
        )

        # Stage 6: Final polish for strict format compliance
        polished_solution = await self.revise(
            instruction="""Final revision for strict compliance:
            - Ensure ONLY the function implementation is returned (no extra text, comments, or markdown)
            - Verify function name matches exactly what's in the problem
            - Confirm all necessary imports are present and inside the function if required
            - Ensure return type matches specification (tuple vs list vs dict)
            - Remove any debug prints or extra outputs
            Return ONLY the clean function code, nothing else.""",
            context=final_solution
        )

        return polished_solution