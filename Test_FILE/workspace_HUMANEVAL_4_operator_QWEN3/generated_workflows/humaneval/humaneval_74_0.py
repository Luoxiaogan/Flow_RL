# Workflow ID: humaneval_74_0
# Benchmark: humaneval
# Data Indices: [64, 0]

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
        # Import only what might be needed, dynamically
        import asyncio
        import re

        # PHASE 1: META-ANALYSIS - Understand the problem deeply
        analysis_instructions = """
        Perform a comprehensive structural analysis of the coding problem. Identify:
        1. Input types and structures (string, list, numbers, etc.)
        2. Output type and format requirements
        3. Key transformation rules or algorithms implied by examples
        4. Special conditions or edge cases (like 'y' being vowel only at end)
        5. Whether the problem involves: counting, filtering, comparing, pattern matching, etc.
        6. Any mathematical operations, thresholds, or tolerances
        7. Case sensitivity or normalization requirements
        8. Potential hidden edge cases not shown in examples
        Present as a structured, detailed analysis.
        """

        # Generate 3 independent analyses in parallel for robustness
        analysis_tasks = [
            self.generate(instruction=analysis_instructions, context="")
            for _ in range(3)
        ]
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Ensemble into unified problem understanding
        unified_analysis = await self.ensemble(
            instruction="""
            Synthesize these three analyses into one comprehensive, coherent problem understanding.
            Resolve any contradictions by choosing the most complete and logically consistent interpretation.
            Highlight the core algorithmic approach needed and critical edge cases to handle.
            """,
            contexts_list=analyses
        )

        # PHASE 2: STRATEGY SELECTION - Determine solution approach
        strategy = await self.generate(
            instruction=f"""
            Based on this analysis:
            {unified_analysis}
            
            Select the most appropriate solution strategy from these categories:
            - ITERATIVE_COUNTING: For problems counting elements with conditions
            - PAIRWISE_COMPARISON: For problems comparing elements against thresholds
            - PATTERN_MATCHING: For regex or substring based problems
            - MATHEMATICAL_FORMULA: For problems solvable with direct calculation
            - STATE_MACHINE: For problems requiring state tracking
            
            Also identify what Python constructs will be most useful (loops, comprehensions, built-ins).
            Return ONLY the strategy name and key implementation notes.
            """,
            context=unified_analysis
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION
        solution_instruction_template = """
        Implement the function as specified, using a {approach} approach.
        Key requirements from analysis:
        {analysis_summary}
        
        Guidelines:
        - Match ENTRY POINT function name exactly
        - Handle all edge cases mentioned in analysis
        - Return correct type (int, float, bool, etc.) as shown in examples
        - Keep code minimal—no extra functionality
        - Include necessary conditionals for special cases
        - Use clear, direct logic over clever optimizations
        """

        # Generate multiple solution variants based on strategy
        if "ITERATIVE_COUNTING" in strategy or "PAIRWISE_COMPARISON" in strategy:
            variants = 2
        else:
            variants = 1

        solution_tasks = []
        for i in range(variants):
            approach_desc = "direct iterative" if i == 0 else "comprehension-based"
            solution_instruction = solution_instruction_template.format(
                approach=approach_desc,
                analysis_summary=unified_analysis[:500]  # Truncate if too long
            )
            solution_tasks.append(
                self.generate(instruction=solution_instruction, context=unified_analysis)
            )

        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 4: CRITIQUE & REFINEMENT
        refined_solutions = []
        for i, solution in enumerate(raw_solutions):
            critique = await self.generate(
                instruction=f"""
                Critically evaluate this solution against the original problem specification:
                - Does it handle all examples shown in docstring?
                - Are edge cases from analysis properly addressed?
                - Is return type correct?
                - Is function name exactly as ENTRY POINT?
                - Are there any logical errors or oversights?
                - Could it fail on unshown edge cases?
                
                If issues found, describe them specifically. If perfect, say "NO ISSUES".
                """,
                context=solution
            )
            
            if "NO ISSUES" not in critique.upper():
                refined = await self.revise(
                    instruction=f"""
                    Revise the solution to fix these issues:
                    {critique}
                    
                    Maintain exact function signature and ENTRY POINT name.
                    Ensure all edge cases are handled.
                    Return only the corrected Python function code.
                    """,
                    context=solution
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(solution)

        # PHASE 5: FINAL SELECTION
        if len(refined_solutions) > 1:
            final_solution = await self.ensemble(
                instruction="""
                Select the best solution from these candidates. Criteria:
                1. Correctness (handles all cases)
                2. Simplicity (minimal, readable code)
                3. Robustness (edge case coverage)
                4. Precision (exact return type, no extras)
                
                Return ONLY the selected Python function code.
                """,
                contexts_list=refined_solutions
            )
        else:
            final_solution = refined_solutions[0]

        # PHASE 6: SANITIZATION - Extract pure function code
        clean_code = await self.summarize(
            instruction="""
            Extract ONLY the Python function implementation from this text.
            - Must start with 'def function_name(...):'
            - Must include exactly the function body
            - Remove any markdown, explanations, or extra text
            - Ensure function name matches ENTRY POINT exactly
            - Preserve all indentation and structure
            Return ONLY the clean Python code, nothing else.
            """,
            context=final_solution
        )

        return clean_code