# Workflow ID: mgsmbn_61_0
# Benchmark: mgsmbn
# Data Indices: [34]

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

        # Step 1: Hierarchical Decomposition with Dependency Tracking
        decomposition_instruction = """
        Break down this Bengali math problem into atomic, computable subproblems.
        Each subproblem must:
        - Represent a single calculable step (e.g., "compute Tuesday's articles")
        - Specify its dependencies (which subproblems must be solved first)
        - Include the relevant entities, units, and operations
        - Preserve chronological or logical order
        - Handle proportional phrases (like "2/5 গুণ বেশি") as separate interpretation steps
        
        Format each subproblem as:
        {
            "id": "step_1",
            "description": "Clear description of what to compute",
            "dependencies": "comma-separated IDs of prerequisites"
        }
        
        Example for "Tuesday has 2/5 times more than Monday":
        - step_1: "Extract Monday's base value (5 articles)"
        - step_2: "Interpret '2/5 গুণ বেশি' as multiplicative factor (1 + 2/5 = 7/5)"
        - step_3: "Compute Tuesday's articles: 5 * 7/5 = 7"
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Step 2: Parallel Semantic Interpretation for Ambiguous Phrases
        ambiguous_phrases = []
        for sp in subproblems:
            if any(term in sp['description'] for term in ['গুণ বেশি', 'অংশ', 'ভগ্নাংশ', 'অনুপাত']):
                ambiguous_phrases.append(sp)

        if ambiguous_phrases:
            interpretation_tasks = []
            for phrase in ambiguous_phrases:
                interpret_instruction = f"""
                Interpret this ambiguous Bengali mathematical phrase in context:
                "{phrase['description']}"
                
                Consider:
                - Does "X গুণ বেশি" mean (1 + X) times or just X times?
                - Are fractions representing parts of a whole or multiplicative factors?
                - What are the units and entities involved?
                - What interpretation yields integer results where expected?
                - What aligns with real-world plausibility?
                
                Provide 2-3 plausible mathematical interpretations with justifications.
                """
                interpretation_tasks.append(
                    self.generate(instruction=interpret_instruction, context="")
                )
            
            interpretations = await asyncio.gather(*interpretation_tasks)
            
            # Ensemble to select best interpretation
            for i, phrase in enumerate(ambiguous_phrases):
                ensemble_instruction = f"""
                Select the most contextually appropriate mathematical interpretation for:
                "{phrase['description']}"
                
                Criteria:
                1. Unit consistency (e.g., articles should be integers)
                2. Real-world plausibility
                3. Alignment with problem's chronological/logical flow
                4. Mathematical soundness
                
                Justify your selection.
                """
                selected_interpretation = await self.ensemble(
                    instruction=ensemble_instruction,
                    contexts_list=[interpretations[i]]
                )
                
                # Update subproblem description with resolved interpretation
                for sp in subproblems:
                    if sp['id'] == phrase['id']:
                        sp['description'] += f" [INTERPRETED AS: {selected_interpretation}]"

        # Step 3: Generate Symbolic Pseudocode for Verification
        pseudocode_instruction = f"""
        Convert the decomposed subproblems into symbolic mathematical pseudocode.
        For each subproblem:
        - Define variables with units (e.g., monday_articles = 5)
        - Write equations with clear operators
        - Track dependencies (e.g., tuesday_articles = monday_articles * 1.4)
        - Include validation rules (e.g., "must be integer", "must be positive")
        
        Subproblems:
        {json.dumps(subproblems, indent=2, ensure_ascii=False)}
        
        Output format:
        VARIABLES:
        - var_name: value # unit and description
        
        EQUATIONS:
        - step_id: equation # justification
        
        VALIDATION:
        - step_id: validation_rule
        """
        
        pseudocode = await self.generate(
            instruction=pseudocode_instruction,
            context=""
        )

        # Step 4: Parallel Solution Attempts with Different Strategies
        # Strategy 1: Direct Computation
        direct_compute_instruction = f"""
        Generate Python code to solve this problem using direct computation.
        Use the pseudocode as reference:
        {pseudocode}
        
        Requirements:
        - Define all variables explicitly
        - Include unit tracking in variable names (e.g., hours_per_article)
        - Validate intermediate results (assert integer where required)
        - Handle edge cases (negative values, division by zero)
        - Print final answer as a single number
        """
        
        # Strategy 2: Algebraic Modeling
        algebraic_instruction = f"""
        Generate Python code to solve this problem using algebraic modeling.
        Instead of direct computation, set up equations and solve symbolically.
        Use the pseudocode as reference:
        {pseudocode}
        
        Requirements:
        - Use sympy for symbolic computation if needed
        - Define symbols for unknowns
        - Solve system of equations
        - Validate solution against constraints
        - Print final answer as a single number
        """
        
        # Run both strategies in parallel
        direct_solution = self.programmer(
            instruction=direct_compute_instruction,
            context=pseudocode
        )
        algebraic_solution = self.programmer(
            instruction=algebraic_instruction,
            context=pseudocode
        )
        
        solutions = await asyncio.gather(direct_solution, algebraic_solution)

        # Step 5: Ensemble to Reconcile Solutions
        ensemble_instruction = """
        Compare these two solution attempts:
        1. Direct computation approach
        2. Algebraic modeling approach
        
        Evaluate:
        - Do they agree on the final answer?
        - Which approach has fewer assumptions?
        - Which handles edge cases better?
        - Which is more aligned with the problem's structure?
        
        If they agree, select the answer.
        If they disagree, identify the source of discrepancy and select the more robust solution.
        
        Output ONLY the final numerical answer as a single number.
        """
        
        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=solutions
        )

        # Step 6: Meta-Cognitive Plausibility Check
        sanity_check_instruction = f"""
        Perform a plausibility check on this answer: {final_answer}
        
        Consider:
        - Does it match the problem's scale? (e.g., hours in a week, reasonable article counts)
        - Are units consistent? (e.g., not mixing hours with articles)
        - Does it satisfy all constraints mentioned in the problem?
        - Is it within expected bounds? (e.g., positive, non-zero where appropriate)
        
        If implausible, flag with "REVISION NEEDED: [reason]".
        If plausible, output "PLAUSIBLE: [answer]".
        """
        
        sanity_check = await self.generate(
            instruction=sanity_check_instruction,
            context=final_answer
        )

        # Step 7: Iterative Refinement if Needed
        if "REVISION NEEDED" in sanity_check:
            # Trigger revision of decomposition
            revised_decomposition = await self.revise(
                instruction=f"""
                Revise the problem decomposition based on this plausibility error:
                {sanity_check}
                
                Consider:
                - Did we misinterpret any phrases?
                - Did we miss any constraints?
                - Are there hidden steps?
                - Should we adjust our unit handling?
                
                Output revised subproblems in the same format.
                """,
                context=json.dumps(subproblems, indent=2, ensure_ascii=False)
            )
            
            # Re-run computation with revised decomposition
            # (Simplified for brevity - in practice, would recurse or loop)
            final_answer = await self.generate(
                instruction="Given the revision, compute the correct answer.",
                context=revised_decomposition
            )

        # Extract numerical answer
        answer_extraction_instruction = f"""
        Extract the final numerical answer from this text:
        {final_answer}
        
        Rules:
        - Remove any units or explanatory text
        - Return only the number (integer or decimal)
        - If multiple numbers, select the one that answers the main question
        - If no clear number, return 0 as fallback
        """
        
        clean_answer = await self.generate(
            instruction=answer_extraction_instruction,
            context=final_answer
        )

        return clean_answer.strip()