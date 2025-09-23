# Workflow ID: limr_118_0
# Benchmark: limr
# Data Indices: [321, 259]

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

        # STEP 1: CLASSIFY PROBLEM & GENERATE STRATEGIES
        classification = await self.generate(
            instruction="""Thoroughly analyze the mathematical domain and structure of this problem. Identify:
            - Primary mathematical field (algebra, geometry, combinatorics, number theory, etc.)
            - Key entities: variables, constants, functions, geometric objects
            - Constraints and given conditions
            - Expected answer format (must be integer 000-999)
            - At least three distinct solution strategies with brief rationale for each
            - Potential pitfalls or non-obvious insights required
            Format as a structured report with clear section headers.""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON CLASSIFICATION
        strategy_paths = []
        
        if "geometry" in classification.lower() or "triangle" in classification.lower() or "coordinate" in classification.lower():
            # GEOMETRIC PATHWAY
            geo_strategy = await self.generate(
                instruction=f"""Given this geometric classification:
                {classification}
                
                Develop a detailed solution plan using coordinate geometry or vector methods:
                - Assign optimal coordinate system
                - Express all given lengths and constraints as equations
                - Identify target quantity (e.g., BD) as solvable variable
                - Outline algebraic steps to isolate target
                Include specific formulas (distance, law of cosines, etc.) to be applied.""",
                context=classification
            )
            strategy_paths.append(geo_strategy)
            
        if "algebra" in classification.lower() or "polynomial" in classification.lower() or "root" in classification.lower():
            # ALGEBRAIC PATHWAY
            alg_strategy = await self.generate(
                instruction=f"""Given this algebraic classification:
                {classification}
                
                Develop a solution plan using symmetric functions, Vieta's formulas, or polynomial identities:
                - Express target expression in terms of elementary symmetric polynomials
                - Substitute known sums/products of roots
                - Factor or group terms for simplification
                - Identify computational shortcuts or substitutions
                Show how to reduce to arithmetic computation.""",
                context=classification
            )
            strategy_paths.append(alg_strategy)
            
        if "combinatorics" in classification.lower() or "counting" in classification.lower() or "probability" in classification.lower():
            # COMBINATORIAL PATHWAY
            comb_strategy = await self.generate(
                instruction=f"""Given this combinatorial classification:
                {classification}
                
                Develop solution using combinatorial principles:
                - Define sample space and event space precisely
                - Apply counting principles (inclusion-exclusion, recursion, generating functions)
                - Simplify using combinatorial identities
                - Convert to closed-form expression for computation
                Specify any modular arithmetic or divisibility constraints.""",
                context=classification
            )
            strategy_paths.append(comb_strategy)

        # If no domain-specific path triggered, use general mathematical approach
        if len(strategy_paths) == 0:
            general_strategy = await self.generate(
                instruction=f"""Given classification:
                {classification}
                
                Develop a general mathematical solution strategy:
                - Break into logical subproblems
                - Apply appropriate theorems or identities
                - Plan computational verification steps
                - Ensure final answer is integer 000-999""",
                context=classification
            )
            strategy_paths.append(general_strategy)

        # STEP 3: PARALLEL SOLUTION ATTEMPTS (DIAMOND PATTERN)
        solution_attempts = []
        
        for i, strategy in enumerate(strategy_paths):
            # Generate detailed solution attempt
            attempt = await self.generate(
                instruction=f"""Execute this solution strategy with full mathematical rigor:
                {strategy}
                
                Requirements:
                - Show all intermediate steps and justifications
                - Maintain exact precision (no approximations)
                - Verify each algebraic manipulation
                - Box final answer as integer between 000 and 999
                - If stuck, state why and suggest alternative approach""",
                context=strategy
            )
            
            # Spawn parallel critic to validate
            critic_task = self.generate(
                instruction=f"""Critically evaluate this solution attempt:
                {attempt}
                
                Check for:
                - Logical errors or gaps in reasoning
                - Arithmetic mistakes
                - Violation of given constraints
                - Non-integer or out-of-range final answer
                - More elegant or efficient approach
                Return "VALID" if flawless, otherwise detailed critique.""",
                context=attempt
            )
            
            # Spawn parallel computational verification
            compute_task = self.programmer(
                instruction=f"""Extract all computable expressions from this solution:
                {attempt}
                
                Write Python code to:
                - Compute numerical values of all intermediate steps
                - Verify final answer is integer 000-999
                - Cross-check with alternative computational method if possible
                Return code and output.""",
                context=attempt
            )
            
            # Run critic and computation in parallel
            critic_result, compute_result = await asyncio.gather(critic_task, compute_task)
            
            # Revise if critic finds issues
            if "VALID" not in critic_result.upper():
                revised_attempt = await self.revise(
                    instruction=f"""Incorporate this critique to fix errors:
                    {critic_result}
                    
                    Also integrate computational verification:
                    {compute_result}
                    
                    Produce corrected, rigorous solution with verified integer answer.""",
                    context=attempt
                )
                solution_attempts.append(revised_attempt)
            else:
                solution_attempts.append(attempt)

        # STEP 4: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""Synthesize all solution attempts into final answer:
            - Select solution that is mathematically rigorous and matches computational verification
            - If multiple valid answers, choose the one with clearest derivation
            - Ensure final answer is integer between 000 and 999
            - If conflict, prefer solution that uses domain-appropriate methods (e.g., geometry for geometric problems)
            - Return ONLY the three-digit integer answer (e.g., "123")""",
            contexts_list=solution_attempts
        )

        # STEP 5: FINAL VALIDATION & FORMATTING
        # Extract just the integer answer using regex
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', final_answer)
            for num in numbers:
                if len(num) == 3:
                    return num
            # Ultimate fallback: return 000 (should never happen)
            return "000"