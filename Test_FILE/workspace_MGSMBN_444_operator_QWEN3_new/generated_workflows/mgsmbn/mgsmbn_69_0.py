# Workflow ID: mgsmbn_69_0
# Benchmark: mgsmbn
# Data Indices: [33, 98]

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

        # PHASE 1: PARALLEL PROBLEM CLASSIFICATION (Diamond Pattern - Fork)
        classification_instructions = [
            """Analyze this Bengali math problem from a mathematical modeling perspective:
            - Identify the core mathematical structure (rate, distribution, comparison, sequence, etc.)
            - What type of equation or relationship governs the problem?
            - What are the key variables and what are we solving for?
            - Are there any hidden steps or implicit calculations?
            Output a structured classification with clear labels.""",
            
            """Analyze this Bengali math problem from a linguistic/narrative perspective:
            - What is the chronological sequence of events?
            - Who/what are the main entities and how do they interact?
            - What quantities are explicitly stated vs. implied?
            - Are there any conditional statements or dependencies?
            Output a narrative breakdown with timeline and entity mapping.""",
            
            """Analyze this Bengali math problem from a constraints and units perspective:
            - What are the physical or logical constraints? (e.g., no negative people, whole numbers only)
            - What units are involved and do they need conversion?
            - What real-world plausibility checks should be applied?
            - Are there any boundary conditions or edge cases?
            Output a constraints and units analysis with validation rules."""
        ]

        classifications = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in classification_instructions]
        )

        # PHASE 2: SYNTHESIZE CLASSIFICATIONS INTO UNIFIED PROBLEM MODEL (Diamond Pattern - Merge)
        unified_model = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, coherent problem model:
            - Resolve any contradictions between perspectives
            - Prioritize interpretations that maintain unit consistency and chronological plausibility
            - Explicitly state: entities, quantities, relationships, constraints, and target variable
            - Flag any remaining ambiguities that need resolution
            Format as a structured JSON-like outline with clear sections.""",
            contexts_list=classifications
        )

        # PHASE 3: GENERATE MULTIPLE SOLUTION APPROACHES IN PARALLEL
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using this problem model:
                {unified_model}
                
                Develop a step-by-step mathematical solution:
                - Show all calculations explicitly
                - Track units throughout
                - Justify each step based on the problem model
                - Box the final answer at the end""",
                context=unified_model
            ),
            self.generate(
                instruction=f"""Using this problem model:
                {unified_model}
                
                Develop an alternative solution using proportional reasoning or algebraic modeling:
                - Set up equations if applicable
                - Solve symbolically before plugging in numbers
                - Verify dimensional consistency
                - Box the final answer at the end""",
                context=unified_model
            )
        )

        # PHASE 4: ENSEMBLE SOLUTIONS WITH ERROR DETECTION
        combined_solution = await self.ensemble(
            instruction="""Compare these two solution approaches:
            - Do they arrive at the same numerical answer?
            - If not, which one respects the problem constraints and units better?
            - Identify any calculation errors or logical flaws in either approach
            - Synthesize the best elements of both into a single correct solution
            - If both are flawed, generate a corrected version
            Output the final verified solution with the answer clearly boxed.""",
            contexts_list=solution_approaches
        )

        # PHASE 5: ADVERSARIAL VALIDATION LOOP (Iterative Refinement)
        current_solution = combined_solution
        for iteration in range(3):  # Maximum 3 refinement cycles
            critique = await self.generate(
                instruction=f"""Critically evaluate this solution:
                {current_solution}
                
                Play devil's advocate - assume this solution is WRONG. Find flaws:
                - Are units handled consistently throughout?
                - Are there arithmetic errors? Check calculations step by step.
                - Does the answer violate any real-world constraints?
                - Are there alternative interpretations of the problem text?
                - Is the chronological sequence respected?
                If no flaws found, state "NO ISSUES FOUND". Otherwise, list specific corrections needed.""",
                context=current_solution
            )
            
            if "NO ISSUES FOUND" in critique.upper() or "NO FLAWS" in critique.upper():
                break
                
            revised_solution = await self.revise(
                instruction=f"""Revise the solution based on this critique:
                {critique}
                
                - Fix all identified errors
                - Maintain clear step-by-step reasoning
                - Keep units explicit
                - Ensure final answer is boxed
                - If critique is invalid, explain why and keep original""",
                context=current_solution
            )
            
            # Only update if revision actually changed content
            if revised_solution.strip() != current_solution.strip():
                current_solution = revised_solution
            else:
                break  # No meaningful changes, exit loop

        # PHASE 6: FINAL VALIDATION AND ANSWER EXTRACTION
        final_validation = await self.generate(
            instruction=f"""Perform final sanity check on this solution:
            {current_solution}
            
            - Does the numerical answer make real-world sense? (e.g., no negative sleep hours)
            - Is it consistent with the scale of the problem? (e.g., profit shouldn't be millions for 20 candles)
            - Does it satisfy all constraints identified in the problem model?
            - Is the answer format correct (single numerical value)?
            If any issues, state them clearly. Otherwise, output ONLY the final numerical answer.""",
            context=current_solution
        )

        # Extract just the numerical answer (robust extraction for various formats)
        # Look for boxed answer, or last number in text
        answer_match = re.search(r'(?:\*\*|\\boxed\{)?([0-9]+\.?[0-9]*)(?:\}\*\*)?', final_validation)
        if answer_match:
            final_answer = answer_match.group(1)
        else:
            # Fallback: find last number in the text
            numbers = re.findall(r'[0-9]+\.?[0-9]*', final_validation)
            final_answer = numbers[-1] if numbers else "0"

        return final_answer