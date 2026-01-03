# Workflow ID: mgsmbn_52_0
# Benchmark: mgsmbn
# Data Indices: [31, 109]

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

        # PHASE 1: PARALLEL DECOMPOSITION (DIAMOND FORK)
        # Generate three independent interpretations: mathematical, narrative, unit-focused
        math_decomp, narrative_recon, unit_mapping = await asyncio.gather(
            self.generate(
                instruction="""Perform mathematical decomposition of the problem:
                1. Extract all numerical values and their contextual meanings.
                2. Identify implied operations (addition, subtraction, multiplication, division).
                3. Determine the sequence of operations based on temporal or logical order.
                4. Highlight the unknown variable being solved for.
                5. Present as a numbered list with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Reconstruct the problem as a simplified narrative:
                1. Retell the story in chronological, step-by-step form.
                2. Explicitly state what is given and what is asked.
                3. Highlight key actions that imply mathematical operations.
                4. Use simple Bengali or English as needed for clarity.
                5. End with a clear restatement of the question.""",
                context=""
            ),
            self.generate(
                instruction="""Map units and constraints:
                1. List all units mentioned (টাকা, ঘণ্টা, টুকরো, জন, etc.) and their relationships.
                2. Identify implicit constraints (e.g., non-negative, integer-only, real-world limits).
                3. Note any conversions needed (e.g., hours to minutes, dozens to units).
                4. Flag any potential unit inconsistencies.
                5. Present as a structured bullet-point list.""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIS (DIAMOND MERGE)
        # Combine the three perspectives into a unified problem model
        synthesized_model = await self.ensemble(
            instruction="""Synthesize the three perspectives into a single coherent problem model:
            - Integrate mathematical operations with narrative sequence.
            - Embed unit constraints into the calculation plan.
            - Resolve any conflicts between perspectives (e.g., if narrative suggests addition but math suggests subtraction, explain why).
            - Output a step-by-step solution plan with:
                Step 1: [Operation] → [Reason from narrative] → [Unit tracking]
                Step 2: ...
            - Conclude with the expected answer format (integer, decimal, unit).""",
            contexts_list=[math_decomp, narrative_recon, unit_mapping]
        )

        # PHASE 3: SPIRAL REFINEMENT (ITERATIVE VALIDATION)
        current_solution = await self.generate(
            instruction=f"""Execute the solution plan from the synthesized model:
            {synthesized_model}
            
            Show all calculations step by step.
            Carry units through each step.
            Box the final answer at the end.
            If any step is ambiguous, state your assumption explicitly.""",
            context=synthesized_model
        )

        for iteration in range(3):  # Max 3 refinement loops
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                - Are all mathematical operations justified by the original problem?
                - Are units consistent and correctly carried through?
                - Does the final answer make sense in the narrative context?
                - Is the answer format correct (integer/decimal, no extra text)?
                - Are there any logical inconsistencies or calculation errors?
                
                If no issues, respond ONLY with "VALID".
                If issues exist, describe them concisely and suggest corrections.""",
                context=current_solution
            )

            if "VALID" in validation.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    {validation}
                    
                    Maintain all correct parts.
                    Only modify what is necessary.
                    Re-box the final answer.""",
                    context=current_solution
                )

        # PHASE 4: FINAL EXTRACTION & CLEANUP
        # Summarize to distill only the essential reasoning
        clean_reasoning = await self.summarize(
            instruction="""Condense the solution into its minimal essential form:
            - Keep only the steps directly leading to the answer.
            - Remove meta-commentary, assumptions, and validation notes.
            - Preserve units and numerical precision.
            - End with the final answer clearly boxed.""",
            context=current_solution
        )

        # Extract the final numerical answer
        final_answer = await self.generate(
            instruction="""From the reasoning below, extract ONLY the final numerical answer.
            - If multiple numbers exist, select the one that directly answers the original question.
            - Remove all units, labels, and text.
            - Return ONLY the number (integer or decimal).
            - If uncertain, return the last computed number that matches the expected unit and context.""",
            context=clean_reasoning
        )

        # Clean the answer (remove any residual text or formatting)
        # Extract first number found in the response
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return the raw response if no number found (shouldn't happen)
            return final_answer.strip()