# Workflow ID: mgsmbn_90_0
# Benchmark: mgsmbn
# Data Indices: [167]

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
        Universal workflow for MGSM Bengali math problems.
        Architecture: Spiral Refinement with Parallel Interpretation & Adversarial Validation
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL SCENE MODELING (Diamond Pattern)
        # Generate three distinct mathematical interpretations
        literal_promise = self.generate(
            instruction="""Construct a literal mathematical model from the Bengali text.
            - Extract ALL numerical values and their associated entities (e.g., 'প্লেট', 'কাপ')
            - Identify explicit operations (addition, subtraction, multiplication, division)
            - Map comparative phrases ('কম', 'বেশি', 'থেকে') to mathematical relationships
            - Do NOT infer missing information - stay strictly literal
            - Format as: Entities: {...} Relationships: {...} Unknowns: {...}""",
            context=""
        )
        
        proportional_promise = self.generate(
            instruction="""Construct a proportional reasoning model from the Bengali text.
            - Identify all ratios, fractions, percentages, or scaling relationships
            - Treat quantities as proportional even if not explicitly stated
            - Convert all units to base units (e.g., dozens to singles)
            - Assume hidden proportional relationships where context suggests
            - Format as: Proportions: {...} Scaling Factors: {...} Derived Quantities: {...}""",
            context=""
        )
        
        unit_promise = self.generate(
            instruction="""Construct a unit-consistency focused model from the Bengali text.
            - Extract all units (টাকা, ডজন, জিনিস, etc.) and convert to consistent base units
            - Identify unit conversion requirements (e.g., আধ ডজন = 6 units)
            - Flag any unit mismatches or missing conversions
            - Calculate dimensional consistency of all operations
            - Format as: Units: {...} Conversions: {...} Consistency Checks: {...}""",
            context=""
        )

        # Resolve conflicting interpretations
        literal_model, proportional_model, unit_model = await asyncio.gather(
            literal_promise, proportional_promise, unit_promise
        )
        
        unified_model = await self.ensemble(
            instruction="""Synthesize the three mathematical models into one coherent representation.
            CRITERIA:
            1. Prioritize unit consistency - reject any model with dimensional errors
            2. Resolve quantity conflicts by choosing values supported by multiple models
            3. Preserve proportional relationships only if explicitly stated or strongly implied
            4. Flag any remaining ambiguities for later validation
            5. Output format: Final Entities, Final Relationships, Final Unknowns, Ambiguities""",
            contexts_list=[literal_model, proportional_model, unit_model]
        )

        # PHASE 2: ADVERSARIAL REVISION (Stress-test the model)
        stress_tested_model = await self.revise(
            instruction="""Act as a skeptical mathematician. Try to break this model:
            - Assume at least one assumption is wrong. Which is most vulnerable?
            - Test edge cases: What if quantities were zero? What if relationships were inverted?
            - Check for real-world plausibility: Can prices be negative? Can people be fractional?
            - Verify unit consistency again after all operations
            - If any flaw found, revise the model accordingly
            - If no flaws, strengthen justification for each relationship
            OUTPUT: Revised Model with Validation Notes""",
            context=unified_model
        )

        # PHASE 3: STEPWISE CALCULATION WITH VALIDATION LOOP
        current_context = stress_tested_model
        max_iterations = 3
        final_answer = None
        
        for iteration in range(max_iterations):
            # Generate step-by-step solution
            stepwise_solution = await self.generate(
                instruction=f"""Generate explicit, numbered calculation steps based on this model:
                {current_context}
                
                REQUIREMENTS:
                - Each step must show full calculation with intermediate values
                - Track units at every step (e.g., 6 plates × 6000 টাকা/plate = 36000 টাকা)
                - Clearly state what each step accomplishes
                - Final step must isolate the unknown and compute it
                - If any step produces implausible result (negative, fractional people, etc.), STOP and flag""",
                context=current_context
            )
            
            # Validate each step
            validation = await self.generate(
                instruction=f"""Validate this stepwise solution:
                {stepwise_solution}
                
                CHECKLIST:
                1. Are all intermediate results plausible? (no negative money, fractional people, etc.)
                2. Do units remain consistent throughout?
                3. Does the final answer match the problem's requested unknown?
                4. Is the magnitude reasonable? (e.g., cup price shouldn't exceed plate price by 100x)
                5. Are there any calculation errors?
                
                OUTPUT: "VALID" if all checks pass, otherwise detailed error description""",
                context=stepwise_solution
            )
            
            if "VALID" in validation.upper() and not any(phrase in validation.upper() 
                   for phrase in ["ERROR", "INVALID", "IMPLAUSIBLE", "MISTAKE"]):
                # Extract final numerical answer
                answer_extraction = await self.generate(
                    instruction=f"""Extract ONLY the final numerical answer from this solution:
                    {stepwise_solution}
                    
                    RULES:
                    - Return ONLY the number (integer or decimal)
                    - No units, no explanation, no punctuation
                    - If multiple numbers, choose the one that answers the problem's question
                    - Example valid outputs: "145", "3.14", "0" """,
                    context=stepwise_solution
                )
                
                # Clean and return answer
                final_answer = re.sub(r'[^\d\.]', '', answer_extraction.strip())
                break
            else:
                # Revise model based on validation feedback
                current_context = await self.revise(
                    instruction=f"""Revise the mathematical model based on these validation errors:
                    {validation}
                    
                    - Fix the identified issues
                    - Strengthen weak assumptions
                    - Add missing constraints
                    - Preserve correct parts of the model
                    OUTPUT: Revised Model""",
                    context=current_context
                )
        else:
            # Fallback: Extract best attempt if loop exhausted
            answer_extraction = await self.generate(
                instruction="""Despite validation issues, extract the most plausible numerical answer.
                Focus on the final calculation step. Return ONLY the number.""",
                context=stepwise_solution
            )
            final_answer = re.sub(r'[^\d\.]', '', answer_extraction.strip())

        # FINAL SAFETY CHECK: Plausibility report (internal use only)
        plausibility_report = await self.generate(
            instruction=f"""Generate a plausibility report for this answer: {final_answer}
            - Does it make sense in real-world context?
            - Is it within reasonable magnitude compared to other quantities in problem?
            - Would a 5th grader find this answer believable?
            - If not, suggest what might be wrong (but don't change the answer)""",
            context=stepwise_solution
        )
        
        # Return final answer (the plausibility report is for internal validation only)
        return final_answer