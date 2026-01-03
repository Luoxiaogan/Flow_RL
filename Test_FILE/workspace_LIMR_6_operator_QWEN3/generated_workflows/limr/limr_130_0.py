# Workflow ID: limr_130_0
# Benchmark: limr
# Data Indices: [49, 267]

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

        # Step 1: Problem Classification and Strategic Framing
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic framing:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Determine the core objective (find value, prove statement, count configurations, etc.)
            3. List all given constraints, conditions, and implicit assumptions
            4. Identify potential solution strategies (at least 3 distinct approaches)
            5. Flag any potential pitfalls or common mistakes for this problem type
            6. Estimate computational complexity and feasibility of brute force
            7. Suggest optimal decomposition strategy
            
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition with Dependencies
        decomposition = await self.decompose(
            instruction=f"""Based on the classification:
            {classification}
            
            Decompose this problem into minimal, solvable subproblems with explicit dependencies.
            Each subproblem should be:
            - Mathematically well-defined
            - As independent as possible (minimize unnecessary dependencies)
            - Ordered by logical prerequisite (what must be solved before what)
            - Tagged with required mathematical techniques
            
            Return the decomposition as a list of subproblems with IDs and dependency chains.""",
            context=classification
        )

        # Step 3: Parallel Strategy Exploration
        # Extract main approaches from classification for parallel exploration
        strategy_prompts = [
            """Develop a solution using algebraic manipulation and equation solving. 
            Focus on setting up systems of equations, exploiting symmetries, and applying polynomial identities.
            Show all intermediate steps and justify each transformation.""",
            
            """Develop a solution using number theoretic approaches (modular arithmetic, divisibility, 
            prime factorization, etc.). Look for patterns, cycles, and properties that can simplify computation.
            Emphasize theoretical justification over brute force calculation.""",
            
            """Develop a solution using combinatorial or probabilistic reasoning. 
            Consider counting principles, generating functions, or probabilistic interpretations.
            Structure the solution as a logical argument with clear combinatorial interpretations."""
        ]

        # Generate parallel solution attempts
        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{prompt}
                
                IMPORTANT: Base your solution on the problem decomposition:
                {decomposition}
                
                If a particular strategy is clearly inapplicable, state why and pivot to a hybrid approach.
                Show all work and reasoning steps. Flag any uncertain assumptions.""",
                context=classification
            ) for prompt in strategy_prompts]
        )

        # Step 4: Strategy Synthesis and Selection
        synthesized_strategy = await self.ensemble(
            instruction="""Evaluate and synthesize the parallel solution attempts:
            1. Assess each attempt for mathematical soundness, completeness, and efficiency
            2. Identify the most promising approach or create a hybrid of the best elements
            3. Resolve any contradictions between approaches
            4. Create a unified solution roadmap that incorporates the strongest elements
            5. Explicitly state any remaining uncertainties or verification needs
            
            Output a consolidated solution plan with clear next steps.""",
            contexts_list=strategy_attempts
        )

        # Step 5: Targeted Computational Execution (if needed)
        # Check if computation is required and generate precise instructions
        computation_needed = await self.generate(
            instruction=f"""Based on the synthesized strategy:
            {synthesized_strategy}
            
            Determine if precise computation is required to reach the final answer.
            If yes, generate EXACT instructions for the Programmer operator including:
            - Specific mathematical operations to perform
            - Required precision and format
            - Any constraints or boundary conditions
            - Expected output format (must be integer 000-999)
            
            If no computation is needed, output "PURELY ANALYTICAL".""",
            context=synthesized_strategy
        )

        computational_result = ""
        if "PURELY ANALYTICAL" not in computation_needed.upper():
            computational_result = await self.programmer(
                instruction=f"""Execute the following computational task precisely:
                {computation_needed}
                
                IMPORTANT REQUIREMENTS:
                - Use modular arithmetic where appropriate to avoid overflow
                - Show intermediate steps for verification
                - Return ONLY the final integer result (000-999 format)
                - If multiple answers possible, return all and flag for review""",
                context=synthesized_strategy,
                max_retries=3
            )
        else:
            computational_result = "No computation required - solution is purely analytical."

        # Step 6: Iterative Verification and Refinement
        # Combine analytical and computational results for verification
        combined_solution = f"""SYNTHESIZED STRATEGY:
        {synthesized_strategy}

        COMPUTATIONAL RESULT:
        {computational_result}"""

        verified_solution = await self.revise(
            instruction="""Critically verify and refine this solution:
            1. Check all mathematical steps for logical consistency
            2. Verify computational results against analytical expectations
            3. Ensure answer format is correct (integer 000-999)
            4. Test edge cases or special values if applicable
            5. Cross-validate using alternative approaches where possible
            6. If errors found, correct them and explain the correction
            7. If confident, output final answer in format: "FINAL ANSWER: XXX" where XXX is 000-999""",
            context=combined_solution
        )

        # Step 7: Final Answer Extraction and Formatting
        final_answer = await self.generate(
            instruction=f"""Extract and format the final answer from this verified solution:
            {verified_solution}
            
            Requirements:
            - Must be exactly three digits (000-999)
            - If answer is less than 100, pad with leading zeros
            - If answer is greater than 999, this indicates an error - flag for review
            - Output ONLY the three-digit number, nothing else
            - If multiple valid answers, select the most reasonable based on context""",
            context=verified_solution
        )

        # Clean and validate final answer format
        cleaned_answer = re.sub(r'\D', '', final_answer)  # Remove non-digits
        if len(cleaned_answer) > 3:
            # Take last 3 digits if too long (common in modular arithmetic)
            cleaned_answer = cleaned_answer[-3:]
        elif len(cleaned_answer) < 3:
            # Pad with leading zeros
            cleaned_answer = cleaned_answer.zfill(3)
        
        # Final verification that answer is in range
        if int(cleaned_answer) > 999:
            cleaned_answer = str(int(cleaned_answer) % 1000).zfill(3)

        return cleaned_answer