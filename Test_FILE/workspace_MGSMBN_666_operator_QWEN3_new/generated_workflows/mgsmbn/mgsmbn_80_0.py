# Workflow ID: mgsmbn_80_0
# Benchmark: mgsmbn
# Data Indices: [130, 57]

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
        import re

        # Step 1: Classify problem complexity and type
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem and classify it:
            1. Complexity Level: Simple (1-2 operations), Medium (3-4 steps), Complex (5+ steps with dependencies)
            2. Problem Type: Sequential, Rate-based, Proportional, Distribution, Comparison, Multi-entity
            3. Key Challenges: Ambiguous phrasing, Hidden steps, Unit conversions, Temporal sequencing
            4. Required Operations: List all mathematical operations needed (add, subtract, multiply, divide, fractions, percentages)
            5. Units Involved: Identify all units (টাকা, ফুট, কাপ, দিন, etc.) and potential conversion needs
            6. Boundary Conditions: Any real-world constraints (no negative values, whole numbers only, etc.)
            
            Format your response as a structured JSON-like dictionary with these keys.""",
            context=""
        )

        # Step 2: Adaptive decomposition based on complexity
        if "Complex" in classification or "Medium" in classification:
            decomposition = await self.decompose(
                instruction="""Break down this problem into atomic subproblems with explicit dependencies:
                - Each subproblem should be solvable independently given its dependencies
                - Include the mathematical operation required for each
                - Specify input values and expected output format
                - Track unit consistency throughout
                - Flag any ambiguous phrases that need interpretation
                
                Return as list of dictionaries with 'id', 'description', 'dependencies', 'operation', 'units'""",
                context=classification
            )
        else:
            # For simple problems, create a single-step decomposition
            decomposition = [{
                "id": "step1",
                "description": "Solve the entire problem in one step",
                "dependencies": "",
                "operation": "direct_calculation",
                "units": "problem_units"
            }]

        # Step 3: Parallel semantic enrichment of each subproblem
        async def enrich_subproblem(subproblem):
            # Handle ambiguous phrases in parallel
            ambiguity_resolution = await self.generate(
                instruction=f"""Given this subproblem: {subproblem['description']}
                Identify and resolve any linguistic ambiguities:
                - Translate Bengali mathematical phrases to precise operations (e.g., 'দুই তৃতীয়াংশ' → multiply by 2/3)
                - Clarify temporal references ('তারপর থেকে' → after day 180)
                - Resolve pronoun references
                - Confirm unit consistency
                - Check against boundary conditions from classification
                
                Return a clarified version of the subproblem with all ambiguities resolved.""",
                context=f"Classification: {classification}"
            )
            
            # Generate pseudocode narrative
            pseudocode = await self.generate(
                instruction=f"""Convert this clarified subproblem into step-by-step pseudocode:
                - Use clear, imperative language
                - Include variable names that reflect real-world entities
                - Specify data types and units
                - Include error checking for boundary conditions
                - Format as numbered steps
                
                Subproblem: {ambiguity_resolution}""",
                context=ambiguity_resolution
            )
            
            return {
                "original": subproblem,
                "clarified": ambiguity_resolution,
                "pseudocode": pseudocode
            }

        # Process all subproblems in parallel
        enriched_subproblems = await asyncio.gather(
            *[enrich_subproblem(sp) for sp in decomposition]
        )

        # Step 4: Build context tapestry for code generation
        context_tapestry = f"""Problem Classification: {classification}

Enriched Subproblems:
"""
        for i, esp in enumerate(enriched_subproblems):
            context_tapestry += f"\nSubproblem {i+1}:\n{esp['pseudocode']}\n"

        # Step 5: Generate and revise code
        initial_code = await self.generate(
            instruction="""Generate Python code to solve this problem based on the context tapestry:
            - Use clear variable names reflecting real-world entities
            - Include comments explaining each step
            - Implement unit tracking and boundary condition checks
            - Return only the final numerical answer (no text)
            - Handle edge cases gracefully
            - Use exact arithmetic (fractions if needed)
            
            IMPORTANT: The code must output ONLY the numerical answer, nothing else.""",
            context=context_tapestry
        )

        revised_code = await self.revise(
            instruction="""Critically review this code:
            1. Verify mathematical correctness against the original problem
            2. Check unit consistency throughout calculations
            3. Ensure boundary conditions are respected
            4. Confirm the output is a single numerical value
            5. Optimize for clarity and efficiency
            6. Add error handling for edge cases
            
            Return the improved code that outputs ONLY the numerical answer.""",
            context=initial_code
        )

        # Step 6: Execute code with verification
        result = await self.programmer(
            instruction="""Execute this code to solve the Bengali math word problem:
            - Verify the code is safe to execute
            - Run the calculation
            - Return ONLY the numerical result
            - If error occurs, return 'ERROR'""",
            context=revised_code,
            max_retries=3
        )

        # Step 7: Sanity check and confidence verification
        sanity_check = await self.generate(
            instruction=f"""Perform a sanity check on this result: {result}
            1. Does this answer make sense in the real-world context?
            2. Are units consistent with the problem?
            3. Does it satisfy all boundary conditions?
            4. Is the magnitude reasonable given the input values?
            5. Cross-verify with a quick mental calculation if possible
            
            If the answer passes all checks, return 'CONFIRMED: [result]'. 
            If not, return 'REJECTED: [reason]'""",
            context=f"Original problem: {self.problem_text}\n\nCode: {revised_code}"
        )

        # Step 8: Final output with confidence
        if "CONFIRMED" in sanity_check:
            final_answer = re.search(r'CONFIRMED:\s*([0-9.]+)', sanity_check)
            if final_answer:
                return final_answer.group(1)
            else:
                return result  # Fallback
        else:
            # If rejected, try one more time with simplified approach
            fallback = await self.programmer(
                instruction="""Solve this problem with a direct, simplified approach:
                - Focus only on the core mathematical relationship
                - Ignore complex edge cases
                - Return ONLY the numerical answer""",
                context="",
                max_retries=1
            )
            return fallback