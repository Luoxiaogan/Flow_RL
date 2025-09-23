# Workflow ID: mgsmbn_126_0
# Benchmark: mgsmbn
# Data Indices: [2, 1]

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

        # PHASE 1: SEMANTIC DECOMPOSITION - Extract mathematical primitives
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Identify:
            1. All numerical values with their explicit units (টাকা, মিটার, ঘণ্টা, etc.)
            2. The unknown quantity being asked for (with expected unit)
            3. Mathematical operations implied by verbs and context (দৌড়ান = multiplication of distance, বৃদ্ধি পেল = percentage increase, etc.)
            4. Temporal or logical sequence of events
            5. Constraints (non-negative, integer-only, real-world plausibility)
            6. Hidden relationships (e.g., "150% increase" means multiply by 2.5, not 1.5)
            
            Structure your output as:
            KNOWN: [list with units]
            UNKNOWN: [description with expected unit]
            OPERATIONS: [sequence with justification]
            CONSTRAINTS: [list]
            HIDDEN_RULES: [list of inferred mathematical transformations]""",
            context=""
        )

        # PHASE 2: PARALLEL HYPOTHESIS GENERATION - Three independent solution approaches
        hypothesis_tasks = [
            self.generate(
                instruction=f"""APPROACH 1: Literal Translation + Direct Calculation
                Using the decomposition: {decomposition}
                
                Translate the Bengali problem literally into mathematical expressions.
                Perform step-by-step calculations without interpretation.
                Show all intermediate steps with units.
                Do not simplify until final step.
                Format: Step 1: [calculation] = [result] [unit]""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""APPROACH 2: Contextual Inference + Real-World Modeling
                Using the decomposition: {decomposition}
                
                Interpret the problem in real-world context. What would make practical sense?
                Adjust mathematical operations based on real-world plausibility (e.g., no negative distances).
                Explicitly state assumptions made.
                Show dimensional analysis for each step.
                Format: Assumption: [statement] → Step 1: [calculation] = [result] [unit]""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""APPROACH 3: Formal Equation Setup + Algebraic Solution
                Using the decomposition: {decomposition}
                
                Set up formal equations with variables. Define each variable clearly.
                Solve algebraically step by step.
                Substitute known values only at the end.
                Show unit consistency in each equation.
                Format: Let X = [unknown] → Equation: [expression] → Solution: X = [value] [unit]""",
                context=decomposition
            )
        ]
        
        hypotheses = await asyncio.gather(*hypothesis_tasks)

        # PHASE 3: REFINE EACH HYPOTHESIS WITH MATHEMATICAL RIGOR
        refined_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            refined = await self.revise(
                instruction=f"""CRITICALLY REVISE THIS SOLUTION:
                - Verify each mathematical operation is justified by the original Bengali text
                - Check unit consistency in every step (dimensional analysis)
                - Ensure percentage increases/decreases are calculated correctly (150% increase = ×2.5)
                - Validate against constraints from decomposition
                - Flag any step that seems ambiguous or unsupported
                - Preserve step-by-step format but add [CORRECTED] or [VERIFIED] tags
                
                Original decomposition for reference: {decomposition}""",
                context=hypothesis
            )
            refined_hypotheses.append(refined)

        # PHASE 4: ENSEMBLE SYNTHESIS - Combine best elements from all hypotheses
        synthesized_solution = await self.ensemble(
            instruction="""SYNTHESIZE A SINGLE CORRECT SOLUTION:
            Compare these three refined hypotheses. They may differ in approach but must converge on the same answer.
            Where they agree on operations and values, use that.
            Where they disagree, select the interpretation most consistent with:
            1. Bengali mathematical conventions (e.g., percentage handling)
            2. Real-world plausibility (no negative items, fractional people)
            3. Unit consistency throughout
            4. Explicit verb semantics from original problem
            
            Create a unified step-by-step solution that:
            - Uses the clearest steps from any hypothesis
            - Resolves all conflicts with justification
            - Maintains unit tracking in every step
            - Ends with the final answer clearly stated
            
            Format: Final Solution: Step 1: ... → Step N: ... → Answer: [number] [unit]""",
            contexts_list=refined_hypotheses
        )

        # PHASE 5: META-VALIDATION - Reverse-engineer to verify correctness
        validation = await self.generate(
            instruction=f"""PERFORM REVERSE VALIDATION:
            Given this synthesized solution: {synthesized_solution}
            
            Work backwards: If the final answer is correct, what should the original inputs be?
            Recalculate the problem in reverse step by step.
            Check if you arrive back at the original problem's given values.
            If any discrepancy is found, identify exactly which step is flawed.
            
            Output format:
            REVERSE STEP 1: [calculation] → ... → MATCHES ORIGINAL? [Yes/No]
            ERROR ANALYSIS: [If no, describe exact issue]""",
            context=synthesized_solution
        )

        # PHASE 6: CONDITIONAL REFINEMENT - Only if validation fails
        final_solution = synthesized_solution
        if "No" in validation or "discrepancy" in validation.lower() or "error" in validation.lower():
            final_solution = await self.revise(
                instruction=f"""RE-ANALYZE WITH ERROR CORRECTION:
                Previous solution failed reverse validation: {validation}
                
                Re-examine the original Bengali text for misinterpreted verbs or relationships.
                Common errors: 
                - Percentage increase (150% increase = ×2.5, not ×1.5)
                - Unit conversion errors
                - Sequence misordering (did event A happen before B?)
                
                Generate a corrected solution addressing the specific error identified.
                Show extra verification steps for the problematic part.
                
                Original decomposition for reference: {decomposition}""",
                context=synthesized_solution
            )

        # PHASE 7: ANSWER EXTRACTION - Distill to single numerical value
        final_answer = await self.summarize(
            instruction="""EXTRACT FINAL NUMERICAL ANSWER:
            From the solution below, extract ONLY the final numerical value.
            Remove all text, units, explanations, and intermediate steps.
            If multiple numbers exist, select the one that directly answers the original question.
            Output format: [number only, no text, no units, no punctuation]""",
            context=final_solution
        )

        # Clean and return - ensure pure numeric output
        # Remove any remaining non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        return cleaned_answer