# Workflow ID: mgsmbn_15_0
# Benchmark: mgsmbn
# Data Indices: [104, 30]

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

        # PHASE 1: PARALLEL SEMANTIC EXTRACTION (DIAMOND FORK)
        entity_extraction_task = self.generate(
            instruction="""Extract all entities, quantities, and units from the Bengali problem text. 
            - List every named object, person, or concept.
            - Extract every numerical value and its associated unit (টাকা, ফুট, টি, etc.).
            - Note the role of each quantity (price, distance, count, rate, etc.).
            - Preserve original Bengali terms alongside translations if ambiguous.
            Format as a structured list with clear labels.""",
            context=""
        )
        
        relationship_mapping_task = self.generate(
            instruction="""Map all mathematical relationships and dependencies.
            - For each quantity, identify what it depends on (e.g., 'three times', '5 less than').
            - Translate Bengali relational phrases into mathematical operations (+, -, ×, ÷).
            - Identify order of operations if sequence matters (e.g., 'first A then B').
            - Flag any ambiguous or potentially misinterpreted phrases.
            Output as a dependency graph in text form with operation labels.""",
            context=""
        )
        
        constraint_identification_task = self.generate(
            instruction="""Identify all explicit and implicit constraints.
            - Physical constraints (e.g., no negative people, money can't be negative).
            - Logical constraints (e.g., 'must be integer', 'less than X').
            - Contextual boundaries (e.g., 'within 1000 feet', 'at least 5 items').
            - Unit consistency requirements.
            List each constraint with its justification from the problem text.""",
            context=""
        )
        
        # Execute all three in parallel
        entity_analysis, relationship_analysis, constraint_analysis = await asyncio.gather(
            entity_extraction_task,
            relationship_mapping_task,
            constraint_identification_task
        )

        # PHASE 2: ENSEMBLE SYNTHESIS INTO MATHEMATICAL BLUEPRINT
        mathematical_blueprint = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent mathematical model.
            - Combine entities, relationships, and constraints into a step-by-step solution plan.
            - Define variables for unknowns.
            - Write out the sequence of calculations needed, with justifications.
            - Include unit tracking at each step.
            - Highlight any assumptions made to resolve ambiguities.
            Output as a numbered procedural plan with embedded equations and constraints.""",
            contexts_list=[entity_analysis, relationship_analysis, constraint_analysis]
        )

        # PHASE 3: CASCADE WITH ADVERSARIAL VALIDATION LOOP
        current_solution = mathematical_blueprint
        max_iterations = 3
        final_answer = None

        for iteration in range(max_iterations):
            # Generate candidate numerical solution
            candidate_solution = await self.generate(
                instruction=f"""Execute the mathematical plan step by step.
                - Show all intermediate calculations.
                - Track units throughout.
                - Apply constraints to validate intermediate results.
                - If any step violates a constraint, note it immediately.
                - Output the final numerical answer at the end, clearly labeled.
                Mathematical Plan:
                {mathematical_blueprint}""",
                context=current_solution
            )

            # Spawn adversarial validator
            critique = await self.generate(
                instruction=f"""Critically analyze this solution for errors:
                - Check arithmetic accuracy.
                - Verify unit consistency.
                - Ensure constraint compliance.
                - Validate operation order (e.g., multiplication before addition).
                - Flag any logical leaps or unsupported assumptions.
                - If answer is negative or non-integer in context where it shouldn't be, flag it.
                Be brutally honest. If no errors, state 'NO ISSUES FOUND'.
                Solution to critique:
                {candidate_solution}""",
                context=candidate_solution
            )

            if "NO ISSUES FOUND" in critique.upper() or iteration == max_iterations - 1:
                # Accept solution or take last attempt
                final_answer_text = candidate_solution
                break
            else:
                # Revise and iterate
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix all issues raised in the critique.
                    Critique:
                    {critique}
                    Original Solution:
                    {candidate_solution}
                    Maintain mathematical integrity while correcting errors.
                    Output the revised complete solution.""",
                    context=candidate_solution
                )

        # PHASE 4: FINAL ANSWER EXTRACTION
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - If decimal, use dot notation (e.g., 15.5).
            - If integer, output without decimal point.
            - NO units. NO explanations. NO additional text.
            - If multiple numbers, choose the one that answers the main question.
            - If uncertain, output 0.
            Text:
            """ + final_answer_text,
            context=final_answer_text
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Ensure it's a valid number
        try:
            float(cleaned_answer)
            return cleaned_answer
        except:
            return "0"