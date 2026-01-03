# Workflow ID: mgsmbn_64_0
# Benchmark: mgsmbn
# Data Indices: [137, 106]

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

        # PHASE 1: Problem Understanding & Classification
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math problem:
            1. Identify all numerical values and their associated entities (people, time periods, objects, currency)
            2. Extract key verbs and relationships (increase, decrease, total, per day, remaining, etc.)
            3. Classify problem type: Sequential, Rate-Based, Proportional, Distribution, or Comparison
            4. Infer implicit constraints (e.g., people must be whole numbers, distances non-negative)
            5. Identify what is being asked for (target variable)
            6. Note any potential ambiguities in phrasing
            Output in structured JSON-like format with clear sections.""",
            context=""
        )

        # PHASE 2: Parallel Solution Strategy Generation
        strategy_instructions = [
            """Develop an ALGEBRAIC solution:
            - Define variables for unknowns
            - Write equations based on relationships
            - Solve step-by-step with substitution/elimination
            - Show all intermediate calculations
            - Box final answer""",
            
            """Develop a CHRONOLOGICAL/TABULAR solution:
            - Break problem into time steps or entity-specific calculations
            - Create a mental table of values (day-by-day, person-by-person)
            - Accumulate or compare as specified
            - Show running totals or differences
            - Box final answer""",
            
            """Develop a PROPORTIONAL/UNIT RATE solution:
            - Identify base rates (per day, per item, per person)
            - Scale up/down based on given multipliers
            - Handle unit conversions if needed
            - Verify dimensional consistency
            - Box final answer"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # PHASE 3: Independent Validation & Error Correction
        validation_tasks = []
        for i, attempt in enumerate(solution_attempts):
            validation_task = self.generate(
                instruction=f"""CRITICALLY VALIDATE Solution {i+1}:
                - Check arithmetic at each step (show recalculations if needed)
                - Verify unit consistency (miles, dollars, people, etc.)
                - Ensure answer matches problem's requested quantity
                - Flag any physically impossible intermediates (negative people, fractional days)
                - Assess whether interpretation of Bengali phrasing is justified
                - If error found, suggest correction; if valid, confirm with "VALID"
                Output detailed validation report.""",
                context=attempt
            )
            validation_tasks.append(validation_task)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # PHASE 4: Revise Solutions Based on Validation Feedback
        revised_solutions = []
        for i, (attempt, validation) in enumerate(zip(solution_attempts, validation_results)):
            if "error" in validation.lower() or "invalid" in validation.lower():
                revised = await self.revise(
                    instruction=f"""INCORPORATE VALIDATION FEEDBACK:
                    Original solution: {attempt}
                    Validation feedback: {validation}
                    
                    REVISE by:
                    - Correcting any arithmetic or logical errors
                    - Adjusting misinterpreted relationships
                    - Adding missing steps or constraints
                    - Ensuring final answer is boxed and matches required format
                    Output fully corrected solution.""",
                    context=attempt
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(attempt)  # No revision needed

        # PHASE 5: Ensemble Synthesis with Sanity Check
        # Generate quick estimation for cross-verification
        estimation = await self.generate(
            instruction="""Generate a QUICK ORDER-OF-MAGNITUDE ESTIMATE:
            - Round numbers to nearest easy values
            - Perform rough mental math
            - Should take <10 seconds to compute
            - Output only the estimated number (no explanation)
            Example: If problem involves 23 days at $47/day, estimate 20*50 = 1000""",
            context=problem_analysis
        )

        final_answer = await self.ensemble(
            instruction=f"""SYNTHESIZE BEST ANSWER with SANITY CHECK:
            Available solutions: {revised_solutions}
            Quick estimate: {estimation}
            
            Selection criteria:
            1. Mathematical correctness (validated steps)
            2. Consistency with problem constraints and Bengali phrasing
            3. Alignment with quick estimate (must be within reasonable range)
            4. Clarity and completeness of derivation
            
            If all solutions agree and match estimate → select any
            If disagreement → pick most consistent with validation reports
            If none match estimate → trigger error protocol (return estimate with warning)
            
            OUTPUT ONLY THE FINAL NUMERICAL ANSWER (integer or decimal). NO TEXT.""",
            contexts_list=revised_solutions
        )

        # PHASE 6: Final Formatting & Extraction (ensure pure number output)
        clean_answer = await self.generate(
            instruction="""EXTRACT ONLY THE NUMERICAL ANSWER:
            Input may contain text, explanations, or boxed answers.
            Extract the final numerical value (integer or decimal).
            Remove any units, text, or formatting.
            If multiple numbers, pick the one that answers the question.
            If no clear number, return 0.
            OUTPUT ONLY THE NUMBER.""",
            context=final_answer
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', clean_answer.strip())
        # Handle edge case where multiple dots exist
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = parts[0] + '.' + ''.join(parts[1:])
        
        return cleaned if cleaned else "0"