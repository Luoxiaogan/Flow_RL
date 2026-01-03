# Workflow ID: mgsmbn_45_0
# Benchmark: mgsmbn
# Data Indices: [28]

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

        # PHASE 1: PARALLEL HYPOTHESIS GENERATION (Diamond Pattern)
        # Generate three distinct reasoning strategies in parallel
        hypothesis_instructions = [
            """Adopt a LITERAL INTERPRETATION strategy:
            - Translate each sentence directly into mathematical operations
            - Assume chronological order of events matches text order
            - Explicitly list all numbers and their associated entities
            - Do NOT infer unstated relationships
            - Format: Step-by-step operations with intermediate results""",
            
            """Adopt a REVERSE-ENGINEERING strategy:
            - Start from the final state mentioned in the problem
            - Work backward to determine initial conditions
            - Focus on 'remaining', 'leftover', or 'final amount' clues
            - Assume the final state is correct and deduce what must have happened
            - Format: Backward steps with justifications""",
            
            """Adopt a CONSTRAINT-BASED strategy:
            - Identify all implicit constraints (non-negative quantities, integer people, etc.)
            - List physical/logical boundaries before calculating
            - Prioritize solutions that respect real-world plausibility
            - Flag any operation that might violate constraints
            - Format: Constraints first, then calculations"""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # PHASE 2: VALIDATION & SYNTHESIS (Conditional Cascade)
        validated_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            # Validate each hypothesis against three criteria
            validation_prompt = f"""Critically evaluate this solution hypothesis against:
            1. MATHEMATICAL CONSISTENCY: Do all operations follow correct order? Any arithmetic errors?
            2. UNIT CONSISTENCY: Are units preserved? Any incompatible unit mixing?
            3. CONTEXTUAL PLAUSIBILITY: Does the answer make sense in real-world context?
            
            If any criterion fails, explain exactly what's wrong and how to fix it.
            If all pass, output 'VALID' followed by the hypothesis.
            
            Hypothesis to validate:
            {hypothesis}"""
            
            validation = await self.generate(instruction=validation_prompt, context=hypothesis)
            
            if "VALID" in validation:
                validated_hypotheses.append(hypothesis)
            else:
                # Revise failed hypotheses
                revised = await self.revise(
                    instruction=f"""Fix the identified issues:
                    Validation feedback: {validation}
                    
                    Requirements:
                    - Correct mathematical errors
                    - Ensure unit consistency
                    - Maintain contextual plausibility
                    - Preserve original reasoning strategy""",
                    context=hypothesis
                )
                validated_hypotheses.append(revised)

        # Synthesize best elements from validated hypotheses
        synthesis = await self.ensemble(
            instruction="""Synthesize a unified solution from all validated hypotheses:
            - Combine strongest mathematical approaches
            - Preserve unit tracking from constraint-based approach
            - Incorporate reverse-engineering insights where applicable
            - Output should be a single coherent step-by-step solution
            - Final line must be: "ANSWER: [number]" (extractable by regex)""",
            contexts_list=validated_hypotheses
        )

        # PHASE 3: ITERATIVE CALCULATION WITH UNIT TRACKING (Spiral Refinement)
        final_answer = synthesis
        for iteration in range(3):  # Maximum 3 refinement loops
            # Extract answer for validation
            answer_check = await self.generate(
                instruction=f"""Verify the final answer:
                - Is it a single numerical value?
                - Does it respect all constraints (non-negative, integer if required)?
                - Does it match the problem's required units?
                - If invalid, explain why and suggest correction
                
                Current solution:
                {final_answer}""",
                context=final_answer
            )
            
            if "invalid" not in answer_check.lower() and "error" not in answer_check.lower():
                break  # Valid answer found
            
            # Revise with specific feedback
            final_answer = await self.revise(
                instruction=f"""Correct the answer based on feedback:
                {answer_check}
                
                Requirements:
                - Maintain all correct intermediate steps
                - Fix only the identified issues
                - Ensure final answer is a single number
                - Preserve "ANSWER: [number]" format""",
                context=final_answer
            )

        # Extract final numerical answer
        answer_extraction = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - Look for "ANSWER: [number]" format
            - If not found, extract the last numerical value
            - Return ONLY the number (no units, no text)
            - If decimal, preserve exact precision
            - Example outputs: "42", "3.14", "0" """,
            context=final_answer
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d\.]', '', answer_extraction.strip())
        
        # Handle edge case: if empty, return 0
        if not cleaned_answer:
            return "0"
            
        return cleaned_answer