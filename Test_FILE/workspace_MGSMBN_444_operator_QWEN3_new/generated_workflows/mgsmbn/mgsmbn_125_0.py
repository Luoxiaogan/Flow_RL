# Workflow ID: mgsmbn_125_0
# Benchmark: mgsmbn
# Data Indices: [197, 7]

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

        # PHASE 1: PROBLEM DECOMPOSITION & CLASSIFICATION
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify:
            1. All numerical values and what they represent (entities, quantities, rates, totals)
            2. The unknown being asked for (be specific about what needs to be calculated)
            3. Mathematical relationships (differences, ratios, sums, products, proportions)
            4. Units of measurement and whether conversions are needed
            5. Real-world constraints (integer-only answers, non-negative quantities, etc.)
            6. Classify the problem type: Sequential, Proportional, Distribution, Comparison, or Multi-entity
            7. Suggest 2-3 possible solution strategies with their mathematical basis
            Format as structured markdown with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN)
        solution_strategies = [
            """Solve using step-by-step arithmetic reasoning:
            - Break down into atomic operations
            - Show intermediate results
            - Track units explicitly
            - Verify each step against problem constraints
            - Box final answer at end""",
            
            """Solve using algebraic modeling:
            - Define variables for unknowns
            - Write equations based on relationships
            - Solve symbolically then substitute numbers
            - Check solution against constraints
            - Box final answer at end""",
            
            """Solve using unit analysis and dimensional reasoning:
            - Convert all quantities to base units first
            - Track unit transformations through operations
            - Ensure final answer has correct unit dimension
            - Validate against real-world plausibility
            - Box final answer at end"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{strategy}

                Use the following problem decomposition as context:
                {decomposition}

                IMPORTANT: Show ALL work. Do not skip steps. Handle units carefully. 
                If multiple interpretations are possible, state your assumption explicitly.
                Final answer must be boxed like: \\boxed{{answer}}""",
                context=decomposition
            ) for strategy in solution_strategies]
        )

        # PHASE 3: ENSEMBLE AUDIT & SELECTION
        audited_solution = await self.ensemble(
            instruction="""Act as a mathematical auditor. You are given 3 solution attempts for the same problem.
            Your task:
            1. Compare all solutions for logical consistency
            2. Check unit handling and dimensional correctness
            3. Verify arithmetic calculations (recompute critical steps)
            4. Evaluate against real-world constraints mentioned in decomposition
            5. Identify which solution is most rigorous and error-free
            6. If all have flaws, synthesize a corrected version combining the best elements
            7. Output ONLY the final corrected solution with clear step-by-step reasoning
            8. Ensure final answer is boxed: \\boxed{{answer}}""",
            contexts_list=solution_attempts
        )

        # PHASE 4: ADVERSARIAL REVISION (SELF-CORRECTION)
        refined_solution = await self.revise(
            instruction="""Assume this solution contains at least one subtle error. Your task:
            1. Critically examine each step for:
               - Misinterpreted relationships (e.g., difference vs ratio)
               - Unit conversion mistakes
               - Arithmetic errors in multi-step calculations
               - Violation of implicit constraints (negative quantities, fractional people)
               - Order of operations mistakes
            2. If no error found, state "NO ERRORS FOUND - SOLUTION IS CORRECT"
            3. If error found, provide corrected version with detailed explanation of fix
            4. Maintain boxed final answer format: \\boxed{{answer}}""",
            context=audited_solution
        )

        # PHASE 5: COHERENCE COMPRESSION & VALIDATION
        final_summary = await self.summarize(
            instruction="""Condense this solution into a concise, bullet-point proof:
            - Each bullet must represent one logical step
            - Include only essential calculations
            - Explicitly state any assumptions made
            - Verify final answer matches problem requirements
            - End with boxed answer
            - If any step seems unjustified or unclear, flag it with [REVIEW NEEDED]""",
            context=refined_solution
        )

        # PHASE 6: ANSWER EXTRACTION
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the following solution summary.
            Rules:
            - Return ONLY the number (integer or decimal)
            - No units, no text, no explanations
            - If answer is in box (\\boxed{{}}), extract content inside
            - If multiple numbers, choose the one that answers the original question
            - If uncertain, return the most prominent numerical result
            Example outputs: "42", "3.14", "150" """,
            context=final_summary
        )

        # CLEAN EXTRACTION (remove any accidental text)
        cleaned_answer = re.sub(r'[^\d\.]', '', final_answer.strip())
        
        return cleaned_answer