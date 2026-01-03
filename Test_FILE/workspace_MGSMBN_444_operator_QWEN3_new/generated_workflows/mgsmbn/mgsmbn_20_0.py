# Workflow ID: mgsmbn_20_0
# Benchmark: mgsmbn
# Data Indices: [151, 193]

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

        # Step 1: Problem Classification & Complexity Assessment
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it along multiple dimensions:
            1. Problem Type: Is it a rate problem (interest, speed), distribution (sharing, division), comparison (difference, "how many more"), combinatorial (permutations, exchanges), or sequential (multi-step operations)?
            2. Complexity Level: Simple (direct calculation) or Complex (hidden steps, multiple entities, unit conversions)?
            3. Mathematical Primitives: What core operations are needed? (%, ×, ÷, +, -, fractions, exponents, etc.)
            4. Units & Constraints: What units are involved (টাকা, ঘণ্টা, জিনিস)? Are there implicit constraints (no fractional people, positive quantities only)?
            5. Solution Strategy: What high-level approach is most appropriate? (Step-by-step chronology, algebraic modeling, combinatorial counting, etc.)
            Output a structured JSON-like analysis with clear labels for each dimension.""",
            context=""
        )

        # Step 2: Entity & Relationship Extraction
        entities = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Extract ALL key entities, quantities, and relationships from the problem:
            - People/Objects: Who or what is involved? (e.g., ম্যান্ডি, বেনেডিক্ট, বই)
            - Quantities: All numbers with their semantic meaning (e.g., "100" = principal amount, "2%" = monthly interest rate)
            - Relationships: How entities interact (e.g., "ধার নিয়েছেন" = borrowed, "পড়ে" = reads)
            - Timeline: If time-based, sequence of events (e.g., "3 মাস পরে" = after 3 months)
            Format as a structured list with clear categories.""",
            context=classification
        )

        # Step 3: Parallel Hypothesis Generation (Diamond Pattern)
        # Generate 3 distinct solution approaches based on different reasoning lenses
        hypothesis_tasks = [
            self.generate(
                instruction=f"""Generate a solution using LITERAL INTERPRETATION:
                - Take the problem text at face value.
                - Perform only explicitly stated operations.
                - Do not infer hidden steps.
                - Show all intermediate calculations.
                - Final answer must be a single numerical value.
                Entities & Context: {entities}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Generate a solution using MATHEMATICAL MODELING:
                - Ignore surface narrative; focus on underlying mathematical structure.
                - Use algebra, formulas, or systematic equations.
                - Consider edge cases and constraints.
                - Show derivation steps.
                - Final answer must be a single numerical value.
                Entities & Context: {entities}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Generate a solution using CONTEXTUAL SIMULATION:
                - Simulate the scenario step-by-step as if acting it out.
                - Track state changes over time or interactions.
                - Enforce real-world constraints (no negative books, whole people).
                - Final answer must be a single numerical value.
                Entities & Context: {entities}""",
                context=entities
            )
        ]
        
        hypotheses = await asyncio.gather(*hypothesis_tasks)

        # Step 4: Ensemble Synthesis with Cross-Validation
        synthesized = await self.ensemble(
            instruction="""Synthesize the three solution hypotheses into one final answer:
            1. Compare all three approaches. Where do they agree? Where do they diverge?
            2. Evaluate each hypothesis against:
               - Mathematical correctness (arithmetic, formulas)
               - Unit consistency (are units preserved and appropriate?)
               - Contextual plausibility (does it make sense in the story?)
               - Constraint adherence (no fractional people, positive quantities)
            3. If all agree, select the most clearly reasoned.
            4. If they conflict, pick the one that best satisfies all validation criteria.
            5. If still uncertain, synthesize a hybrid answer or pick the most conservative estimate.
            Output ONLY the final numerical answer as a single number (integer or decimal).""",
            contexts_list=hypotheses
        )

        # Step 5: Iterative Refinement with Validation
        refined = synthesized
        for _ in range(2):  # Max 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically validate this answer against the original problem:
                Answer: {refined}
                
                Check:
                1. Does this answer logically follow from the problem's narrative?
                2. Are all intermediate steps mathematically sound?
                3. Are units handled correctly? (e.g., currency rounded to whole numbers?)
                4. Does it violate any real-world constraints?
                5. Is there a simpler or more direct path to this answer?
                
                If any issues are found, describe them specifically. Otherwise, output 'VALID'.""",
                context=refined
            )
            
            if "VALID" in validation.upper():
                break
            else:
                refined = await self.revise(
                    instruction=f"""Revise the answer based on validation feedback:
                    Validation Issues: {validation}
                    
                    Requirements:
                    - Fix all identified errors.
                    - Maintain clear step-by-step reasoning.
                    - Preserve unit consistency.
                    - Ensure final answer is a single numerical value.
                    - If rounding is needed, follow domain conventions (e.g., whole currency units).""",
                    context=refined
                )

        # Step 6: Final Simulation-Based Sanity Check
        simulation_check = await self.generate(
            instruction=f"""Perform a final narrative simulation:
            Original Problem: {self.problem_text}
            Proposed Answer: {refined}
            
            Re-tell the problem's story in simple Bengali step-by-step, showing how the answer is reached.
            Verify that:
            - Every step in the story is accounted for.
            - No logical leaps or missing operations.
            - The final number makes sense in context.
            
            If simulation fails, output 'REJECT'. Otherwise, output the final answer as a single number.""",
            context=refined
        )

        # Extract final numerical answer (robust parsing)
        final_answer = refined
        if "REJECT" not in simulation_check.upper():
            final_answer = simulation_check

        # Clean and extract number (handle potential text wrappers)
        number_match = re.search(r'[\d\.]+', final_answer)
        if number_match:
            final_answer = number_match.group(0)
            # Convert to int if whole number
            if '.' in final_answer and final_answer.endswith('.0'):
                final_answer = final_answer[:-2]
            elif '.' not in final_answer:
                final_answer = str(int(float(final_answer)))
        else:
            # Fallback: return as-is if no number found (let downstream handle)
            pass

        return final_answer