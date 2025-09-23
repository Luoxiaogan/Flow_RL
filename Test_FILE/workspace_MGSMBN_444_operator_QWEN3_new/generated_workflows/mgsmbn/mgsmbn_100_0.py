# Workflow ID: mgsmbn_100_0
# Benchmark: mgsmbn
# Data Indices: [70]

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

        # STEP 1: PARALLEL DECOMPOSITION (DIAMOND FORK)
        # Analyze problem from 3 independent perspectives simultaneously
        linguistic_analysis, math_analysis, logic_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform deep linguistic analysis of the Bengali problem:
                1. Extract all named entities (people, objects, places) and assign roles.
                2. Identify every numerical value and its contextual meaning (what does it count/measure?).
                3. Map all relational phrases (e.g., 'তিনগুণ বেশি' = three times more, 'থেকে দুটি বেশি' = two more than).
                4. Flag implicit constraints (e.g., pets can't be negative, people counts must be integers).
                5. Identify chronological or causal sequences if present.
                Format as structured bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Perform mathematical structure analysis:
                1. Identify all mathematical operations implied (addition, subtraction, multiplication, division, ratios).
                2. Determine variable dependencies (what unknowns depend on which knowns?).
                3. Sequence operations chronologically or logically.
                4. Identify if algebraic substitution is needed.
                5. Note any unit conversions required.
                Present as numbered steps with mathematical notation where helpful.""",
                context=""
            ),
            self.generate(
                instruction="""Perform logical constraint analysis:
                1. List all real-world constraints (non-negative quantities, integer requirements, physical limits).
                2. Identify boundary conditions or edge cases.
                3. Check for hidden assumptions (e.g., 'equally divided' implies no remainder).
                4. Validate if problem has sufficient information or needs assumptions.
                5. Flag any potential contradictions in the problem statement.
                Format as logical assertions with 'IF...THEN...' structure where applicable.""",
                context=""
            )
        )

        # STEP 2: SYNTHESIS (DIAMOND MERGE)
        # Combine the three perspectives into unified problem representation
        synthesized_analysis = await self.ensemble(
            instruction="""Synthesize the linguistic, mathematical, and logical analyses into a single coherent problem representation:
            1. Resolve any conflicts between perspectives (e.g., if linguistic says 'three times' but math missed it).
            2. Create a master variable map: assign symbols to all quantities and relationships.
            3. Build a dependency graph: which values must be calculated first?
            4. Incorporate all constraints into the mathematical model.
            5. Output a complete problem specification that can be solved algorithmically.
            Format as: 'PROBLEM SPEC: [clear structured description]'""",
            contexts_list=[linguistic_analysis, math_analysis, logic_analysis]
        )

        # STEP 3: STRATEGY SELECTION (CONDITIONAL BRANCH)
        # Classify problem complexity to choose solution depth
        complexity_analysis = await self.generate(
            instruction=f"""Classify problem complexity based on synthesized analysis:
            {synthesized_analysis}
            
            Classify as:
            - SIMPLE: Single operation, no dependencies, no hidden steps.
            - MODERATE: 2-3 sequential operations, clear dependencies.
            - COMPLEX: Multiple entities, hidden steps, algebraic reasoning, or unit conversions.
            
            Also determine:
            - Primary mathematical domain (arithmetic, proportional, distribution, comparison, multi-entity)
            - Expected answer format (integer, decimal, unit)
            - Any special handling needed (e.g., rounding, remainder interpretation)
            
            Output format: 'COMPLEXITY: [level], DOMAIN: [type], FORMAT: [spec]'""",
            context=synthesized_analysis
        )

        # STEP 4: SOLUTION GENERATION
        # Generate step-by-step solution based on complexity
        if "SIMPLE" in complexity_analysis:
            solution_draft = await self.generate(
                instruction=f"""Generate direct solution for simple problem:
                {synthesized_analysis}
                
                - Perform single calculation.
                - Show work minimally.
                - Verify against constraints.
                - Output final answer clearly marked.""",
                context=synthesized_analysis
            )
        else:
            solution_draft = await self.generate(
                instruction=f"""Generate detailed step-by-step solution:
                {synthesized_analysis}
                
                Requirements:
                1. Solve in logical sequence (chronological if time-based).
                2. Show all intermediate calculations with explanations.
                3. Track units throughout.
                4. Apply constraints at each step.
                5. Use algebraic notation where helpful.
                6. Double-check arithmetic at critical steps.
                7. Clearly mark final answer at the end.
                Format: 'STEP 1: ... → Result: ...'""",
                context=synthesized_analysis
            )

        # STEP 5: ADVERSARIAL VALIDATION LOOP (CASCADE WITH FEEDBACK)
        # Validate and revise up to 3 times
        current_solution = solution_draft
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Act as adversarial validator:
                CRITICALLY examine this solution:
                {current_solution}
                
                Check for:
                1. Arithmetic errors (recalculate key steps).
                2. Unit consistency violations.
                3. Constraint violations (negative pets? fractional people?).
                4. Logical sequence errors (solved before known?).
                5. Answer format mismatch.
                6. Missing hidden steps.
                
                If perfect, respond ONLY with 'VALID'.
                If errors found, describe them concisely and suggest fixes.""",
                context=current_solution
            )
            
            if "VALID" in validation.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise solution based on validation feedback:
                    Validation feedback: {validation}
                    
                    Requirements:
                    - Fix all identified errors.
                    - Maintain step-by-step structure.
                    - Preserve clear final answer marking.
                    - Add verification step if helpful.""",
                    context=current_solution
                )

        # STEP 6: FINAL EXTRACTION
        # Extract and clean the final numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution:
            - Remove all text, units, and explanations.
            - If answer is decimal, preserve exact precision.
            - If multiple numbers, select the one that answers the primary question.
            - Output ONLY the number, nothing else.
            Example outputs: '28', '15.5', '0'""",
            context=current_solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Handle edge case: if empty, return 0 (shouldn't happen with proper validation)
        if not cleaned_answer:
            cleaned_answer = "0"
            
        return cleaned_answer