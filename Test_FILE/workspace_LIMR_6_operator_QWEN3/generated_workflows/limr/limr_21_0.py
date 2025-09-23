# Workflow ID: limr_21_0
# Benchmark: limr
# Data Indices: [304, 47]

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

        # STEP 1: META-DECOMPOSITION — Extract problem signature and classify domain
        decomposition_instruction = """
        Analyze the problem to extract its mathematical DNA. Identify:
        1. Primary domain (geometry, number theory, combinatorics, algebra, optimization, sequences)
        2. Key unknowns and what is being asked (angle sum? probability? integer solution?)
        3. Critical constraints or conditions (e.g., "regular polygons", "randomly selected", "exact integer")
        4. Implied operations (angle chasing, modular arithmetic, counting, equation solving)
        5. Potential solution archetypes (symmetry exploitation, recursive relation, coordinate geometry, etc.)
        
        Output a structured summary that can guide parallel strategy generation.
        """
        problem_signature = await self.generate(instruction=decomposition_instruction, context="")

        # STEP 2: PARALLEL STRATEGY GENERATION — Three reasoning lanes
        symbolic_lane_instruction = f"""
        You are an expert in algebraic and symbolic manipulation. Given the problem signature:
        {problem_signature}
        
        Develop a solution approach focusing on:
        - Setting up equations or functional relationships
        - Variable substitution and algebraic simplification
        - Polynomial, exponential, or logarithmic transformations
        - Exploiting identities or symmetries in expressions
        
        Derive a complete solution path. Show all steps. Assume nothing; justify every operation.
        """
        
        combinatorial_lane_instruction = f"""
        You are an expert in combinatorics and discrete probability. Given the problem signature:
        {problem_signature}
        
        Develop a solution approach focusing on:
        - Constructing sample spaces or counting favorable outcomes
        - Using permutations, combinations, or generating functions
        - Applying probabilistic principles (independence, conditional probability)
        - Exploiting symmetry or complementary counting
        
        Derive a complete solution path. Show all steps. Assume nothing; justify every operation.
        """
        
        geometric_lane_instruction = f"""
        You are an expert in geometry and spatial reasoning. Given the problem signature:
        {problem_signature}
        
        Develop a solution approach focusing on:
        - Interpreting diagrams or constructing coordinate systems
        - Applying angle sum properties, congruence, or similarity
        - Using vector operations or trigonometric identities
        - Leveraging properties of regular polygons, circles, or 3D figures
        
        Derive a complete solution path. Show all steps. Assume nothing; justify every operation.
        """

        # Run all three lanes in parallel
        symbolic_attempt, combinatorial_attempt, geometric_attempt = await asyncio.gather(
            self.generate(instruction=symbolic_lane_instruction, context=""),
            self.generate(instruction=combinatorial_lane_instruction, context=""),
            self.generate(instruction=geometric_lane_instruction, context="")
        )

        # STEP 3: INDEPENDENT REVISION — Peer-review each lane
        revision_instruction_template = """
        You are a skeptical peer reviewer. Critically examine the following solution attempt:
        - Verify every mathematical step for correctness
        - Check for hidden assumptions or unjustified leaps
        - Ensure all constraints from the original problem are respected
        - Confirm that the final answer is an integer between 000 and 999
        - If errors are found, correct them rigorously
        
        Output a revised, bulletproof version of the solution.
        """

        revised_symbolic, revised_combinatorial, revised_geometric = await asyncio.gather(
            self.revise(instruction=revision_instruction_template, context=symbolic_attempt),
            self.revise(instruction=revision_instruction_template, context=combinatorial_attempt),
            self.revise(instruction=revision_instruction_template, context=geometric_attempt)
        )

        # STEP 4: CONTEXT WEAVING — Summarize key insights from each lane
        summarize_instruction = """
        Extract the single most critical insight or numerical result from this solution.
        Format as: "Key Insight: [concise statement]" or "Result: [number]".
        Omit derivations; preserve only the core conclusion.
        """
        
        symbolic_insight = await self.summarize(instruction=summarize_instruction, context=revised_symbolic)
        combinatorial_insight = await self.summarize(instruction=summarize_instruction, context=revised_combinatorial)
        geometric_insight = await self.summarize(instruction=summarize_instruction, context=revised_geometric)

        # STEP 5: ENSEMBLE SYNTHESIS — Cross-validate and fuse insights
        ensemble_instruction = f"""
        You are a mathematical synthesis engine. Given three solution perspectives:
        1. Symbolic/Algebraic: {symbolic_insight}
        2. Combinatorial/Probabilistic: {combinatorial_insight}
        3. Geometric/Spatial: {geometric_insight}
        
        And their full derivations:
        - Symbolic: {revised_symbolic}
        - Combinatorial: {revised_combinatorial}
        - Geometric: {revised_geometric}
        
        Synthesize a unified answer by:
        - Identifying numerical consensus (if all lanes agree on a number, that’s likely correct)
        - Resolving conflicts by tracing back to first principles and problem constraints
        - Combining partial insights (e.g., algebraic equation + combinatorial count)
        - Outputting a single, justified integer answer between 000 and 999
        
        If uncertainty remains, flag it explicitly.
        """
        
        synthesized_solution = await self.generate(instruction=ensemble_instruction, context="")

        # STEP 6: META-VALIDATION — Is the solution confident and complete?
        validation_instruction = """
        Critically assess this synthesized solution:
        - Is every step logically airtight?
        - Are there unaddressed edge cases or alternative interpretations?
        - Does the answer format strictly comply (integer 000-999)?
        - Is there any hedging language ("assume", "likely", "approximately")?
        
        If fully confident, output "VALID: [answer]". 
        If uncertain, output "UNCERTAIN: [reason]".
        """
        
        validation_result = await self.generate(instruction=validation_instruction, context=synthesized_solution)

        # STEP 7: ADAPTIVE DEEP DIVE (if uncertain)
        final_answer = None
        if "UNCERTAIN" in validation_result:
            # Trigger targeted deep dive — focus on the weakest component
            deep_dive_instruction = f"""
            The solution is uncertain due to: {validation_result}
            Re-analyze the problem with extreme rigor:
            - Decompose into atomic subproblems
            - Use Programmer for any computational step
            - Cross-validate with alternative methods
            - Output only the final integer answer (000-999), zero-padded if needed
            """
            
            # Use Programmer if computation is suspected to be the issue
            try:
                programmatic_solution = await self.programmer(
                    instruction="Solve the problem computationally. Output only the integer answer.",
                    context=synthesized_solution,
                    max_retries=2
                )
                # Extract integer from programmer output
                match = re.search(r'\b\d{1,3}\b', programmatic_solution)
                if match:
                    final_answer = match.group(0).zfill(3)
            except:
                # Fallback: force ensemble to pick the most consistent numerical result
                fallback_instruction = """
                Given conflicting or uncertain solutions, extract the most frequently occurring integer result.
                If none, pick the one with the most rigorous derivation. Output as 3-digit string.
                """
                final_answer = await self.generate(instruction=fallback_instruction, context=synthesized_solution)
                # Ensure 3-digit format
                match = re.search(r'\b\d{1,3}\b', final_answer)
                if match:
                    final_answer = match.group(0).zfill(3)
                else:
                    final_answer = "000"  # ultimate fallback
        else:
            # Extract answer from validation result
            match = re.search(r'VALID:\s*(\d{1,3})', validation_result)
            if match:
                final_answer = match.group(1).zfill(3)
            else:
                # Fallback extraction from synthesized solution
                match = re.search(r'\b\d{1,3}\b', synthesized_solution)
                final_answer = match.group(0).zfill(3) if match else "000"

        return final_answer