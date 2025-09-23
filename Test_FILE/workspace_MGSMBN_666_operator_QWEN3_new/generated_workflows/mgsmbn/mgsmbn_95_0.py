# Workflow ID: mgsmbn_95_0
# Benchmark: mgsmbn
# Data Indices: [13]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # PHASE 1: SEMANTIC EXTRACTION & CLASSIFICATION
        initial_extraction = await self.generate(
            instruction="""Perform deep semantic extraction of the Bengali word problem. Identify:
            1. All numerical values with their semantic roles (e.g., 'hourly rate', 'total weeks')
            2. All entities (people, objects, time periods) and their relationships
            3. The explicit question being asked
            4. Implicit constraints or assumptions (e.g., 'annual' implies 52 weeks unless specified)
            5. Unit types and required conversions
            Format as structured JSON with keys: entities, values, question, constraints, units""",
            context=""
        )

        problem_classification = await self.generate(
            instruction=f"""Classify this problem based on extracted structure:
            {initial_extraction}
            
            Determine:
            - Problem type: [rate, distribution, comparison, sequential, proportional, multi-entity]
            - Required operations: [addition, subtraction, multiplication, division, percentage, fraction]
            - Complexity level: [simple, moderate, complex]
            - Potential ambiguities or edge cases
            - Expected answer format (integer, decimal, unit)
            Return as JSON with classification metadata""",
            context=initial_extraction
        )

        # PHASE 2: PARALLEL INTERPRETATION & DECOMPOSITION
        interpretation_tasks = [
            self.generate(
                instruction=f"""Generate LITERAL interpretation:
                Translate problem directly without inference. Map each sentence to mathematical expressions.
                Preserve original units and sequence. Flag any unclear references.
                Context: {initial_extraction}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate CONTEXTUAL interpretation:
                Infer implicit relationships and real-world constraints. Adjust for cultural/linguistic nuances.
                Example: 'annual salary' may imply 52 weeks even if not stated.
                Context: {initial_extraction}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate MAXIMALIST interpretation:
                Consider all possible readings, including edge cases and alternative assumptions.
                What if values are ranges? What if units are mixed? What if temporal logic is ambiguous?
                Context: {initial_extraction}""",
                context=""
            )
        ]
        
        literal_interp, contextual_interp, maximalist_interp = await asyncio.gather(*interpretation_tasks)

        # Synthesize best interpretation
        synthesized_interpretation = await self.ensemble(
            instruction="""Select and synthesize the most accurate interpretation:
            - Prioritize contextual accuracy over literal translation
            - Resolve ambiguities using real-world plausibility
            - Preserve mathematical precision
            - Flag any remaining uncertainties for revision
            Return as unified problem representation with clear mathematical mapping""",
            contexts_list=[literal_interp, contextual_interp, maximalist_interp]
        )

        # PHASE 3: DEPENDENCY-AWARE DECOMPOSITION
        subproblems = await self.decompose(
            instruction=f"""Decompose into ordered subproblems:
            Based on synthesized interpretation: {synthesized_interpretation}
            
            Requirements:
            - Each subproblem must be mathematically self-contained
            - Specify dependencies (which subproblems must be solved first)
            - Include unit tracking at each step
            - Handle temporal sequences explicitly (e.g., 'first calculate weekly, then annual')
            - Output as list of dicts with 'id', 'description', 'dependencies', 'units'""",
            context=synthesized_interpretation
        )

        # PHASE 4: ADAPTIVE SOLUTION STRATEGY
        classification_data = json.loads(problem_classification)
        problem_type = classification_data.get("problem_type", "sequential")

        if "rate" in problem_type or "proportional" in problem_type:
            strategy_instruction = """Apply rate normalization strategy:
            - Convert all rates to common units (e.g., hourly → annual)
            - Handle time conversions explicitly
            - Validate unit consistency at each multiplication/division step"""
        elif "distribution" in problem_type:
            strategy_instruction = """Apply distribution strategy:
            - Calculate total quantity first
            - Divide according to specified ratios or equal shares
            - Handle remainders explicitly
            - Validate no fractional entities unless allowed"""
        elif "comparison" in problem_type:
            strategy_instruction = """Apply comparison strategy:
            - Calculate both quantities independently
            - Compute difference or ratio as requested
            - Validate directionality ('how many more' vs 'how many fewer')"""
        else:
            strategy_instruction = """Apply general sequential strategy:
            - Follow chronological or dependency order
            - Validate intermediate results for plausibility
            - Maintain running unit tracking"""

        # PHASE 5: PROGRAMMATIC SOLUTION WITH DOUBLE REVISION
        pre_programming_validation = await self.revise(
            instruction=f"""Validate mathematical model before computation:
            {strategy_instruction}
            
            Check:
            - All values from original problem are accounted for
            - Units are consistent and conversions are explicit
            - Dependencies are respected in calculation order
            - No real-world implausibilities (negative quantities, fractional people)
            - Answer format matches expectation
            Return revised model ready for programming""",
            context=synthesized_interpretation
        )

        program_result = await self.programmer(
            instruction=f"""Generate and execute Python code to solve:
            {strategy_instruction}
            
            Requirements:
            - Use exact arithmetic (no floating point unless necessary)
            - Include unit tracking in variable names
            - Validate intermediate results
            - Return only the final numerical answer
            - Handle edge cases (division by zero, negative results)""",
            context=pre_programming_validation,
            max_retries=3
        )

        # PHASE 6: POST-COMPUTATION SANITY CHECK
        final_validation = await self.revise(
            instruction=f"""Perform reality-check on computed result:
            Original problem: {self.problem_text}
            Computed answer: {program_result}
            
            Validate:
            - Does this answer make sense in real-world context?
            - Are units correct and consistent?
            - Is the magnitude plausible? (e.g., teacher salary in thousands, not millions)
            - Does it match the problem's complexity level?
            - If any doubt, suggest revision or flag for human review
            Return either the validated answer or a revision request""",
            context=program_result
        )

        # PHASE 7: ITERATIVE REFINEMENT (if needed)
        current_answer = final_validation
        for iteration in range(3):
            plausibility_check = await self.generate(
                instruction=f"""Is this answer definitively correct?
                Answer: {current_answer}
                Problem: {self.problem_text}
                
                Return 'YES' if confident, or detailed explanation of doubt if uncertain""",
                context=current_answer
            )
            
            if "YES" in plausibility_check.upper() and "DOUBT" not in plausibility_check.upper():
                break
            else:
                current_answer = await self.revise(
                    instruction=f"""Revise solution based on doubt: {plausibility_check}
                    Re-extract key values, revalidate units, recompute critical steps.
                    Prioritize accuracy over speed.""",
                    context=current_answer
                )
                # Re-run programmer if revision changed the model significantly
                if "recompute" in plausibility_check.lower() or "recalculate" in plausibility_check.lower():
                    current_answer = await self.programmer(
                        instruction="Recompute with revised model",
                        context=current_answer,
                        max_retries=2
                    )

        # Extract final numerical answer
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this text:
            {current_answer}
            
            Rules:
            - Return ONLY digits, decimal points, and minus sign if negative
            - Remove all units, explanations, and formatting
            - If multiple numbers, return the one that answers the original question
            - If no clear answer, return '0' as fallback""",
            context=current_answer
        )

        return final_answer.strip()