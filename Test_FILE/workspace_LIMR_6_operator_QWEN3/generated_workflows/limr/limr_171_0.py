# Workflow ID: limr_171_0
# Benchmark: limr
# Data Indices: [53, 220]

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

        # Step 1: Problem Classification & Strategic Analysis
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic analysis:
            1. Identify the primary mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
            2. Determine the core challenge type (optimization, proof, equation solving, counting, etc.)
            3. List all explicit and implicit constraints
            4. Predict likely solution approaches and their mathematical tools
            5. Estimate difficulty level and potential pitfalls
            6. Suggest 3 distinct strategic angles for attacking the problem
            Format as structured JSON with keys: domain, challenge_type, constraints, approaches, difficulty, pitfalls""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal atomic subproblems:
            - Each subproblem must be independently solvable given its dependencies
            - Identify prerequisite relationships between subproblems
            - Ensure coverage of all aspects: setup, core calculation, edge cases, verification
            - Prioritize subproblems that unlock multiple downstream steps
            - Include at least one computational subproblem suitable for Programmer
            Classification context: {classification}""",
            context=""
        )

        # Step 3: Parallel Strategy Exploration (Diamond Pattern)
        strategy_attempts = []
        strategy_prompts = [
            """Solve using pure algebraic manipulation and symbolic reasoning. Focus on:
            - Variable substitution and equation transformation
            - Leveraging symmetry and invariants
            - Avoiding numerical computation until final steps
            - Maintaining exact symbolic precision throughout""",
            
            """Solve using combinatorial or counting principles. Focus on:
            - Enumerating cases systematically
            - Applying combinatorial identities
            - Using generating functions or recursive relations if applicable
            - Optimizing through symmetry or equivalence classes""",
            
            """Solve using computational/algorithmic approach. Focus on:
            - Designing efficient search or optimization algorithm
            - Bounding the solution space
            - Implementing mathematical constraints as code
            - Verifying results through multiple test cases"""
        ]

        # Generate parallel solution attempts
        raw_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{prompt}
                
                Problem Classification: {classification}
                Subproblem Structure: {json.dumps(decomposition)}
                
                Provide complete step-by-step solution with clear reasoning.
                Highlight key insights and potential error points.
                Format final answer clearly at the end.""",
                context=""
            ) for prompt in strategy_prompts]
        )

        # Step 4: Adversarial Validation & Weakness Analysis
        validated_attempts = []
        for i, attempt in enumerate(raw_attempts):
            validation = await self.generate(
                instruction=f"""Critically analyze this solution attempt:
                1. Verify logical consistency of each step
                2. Check for arithmetic or algebraic errors
                3. Identify unstated assumptions
                4. Test edge cases and boundary conditions
                5. Assess completeness of solution
                6. Rate confidence (1-10) in final answer
                7. Suggest specific improvements if flaws found
                
                Solution Attempt: {attempt}""",
                context=attempt
            )
            
            # Revise if significant issues found
            if "error" in validation.lower() or "flaw" in validation.lower() or "assumption" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Revise this solution based on validation feedback:
                    Validation Feedback: {validation}
                    
                    Requirements:
                    - Fix all identified errors
                    - Address unstated assumptions
                    - Strengthen weak reasoning steps
                    - Maintain original approach unless fundamentally flawed
                    - Preserve correct insights from original attempt""",
                    context=attempt
                )
                validated_attempts.append(revised)
            else:
                validated_attempts.append(attempt)

        # Step 5: Computational Verification (if applicable)
        computational_verification = await self.programmer(
            instruction=f"""Implement computational verification for this problem:
            - Design algorithm to verify or compute solution
            - Handle edge cases and boundary conditions
            - Output should be single integer (000-999 format)
            - Include multiple test cases if possible
            - Explain how code verifies mathematical solution
            
            Problem Context: {self.problem_text}
            Classification: {classification}
            Best Solution Attempt: {validated_attempts[0]}""",
            context="",
            max_retries=3
        )

        # Step 6: Synthesis & Final Answer Extraction
        final_synthesis = await self.ensemble(
            instruction=f"""Synthesize the best solution from all attempts:
            1. Compare all solution attempts and computational verification
            2. Identify consensus answer or resolve discrepancies
            3. Extract final integer answer (000-999 format)
            4. Provide confidence assessment based on:
               - Number of independent methods agreeing
               - Computational verification match
               - Verification depth of each approach
            5. Format final output as: "FINAL_ANSWER: XXX" where XXX is 3-digit integer
            
            Include brief justification for final answer selection.""",
            contexts_list=[computational_verification] + validated_attempts
        )

        # Step 7: Final Answer Extraction & Formatting
        final_answer = await self.generate(
            instruction="""Extract the final 3-digit integer answer from the synthesis:
            - Look for "FINAL_ANSWER: XXX" format
            - If not found, extract any 3-digit number from final conclusion
            - Ensure answer is between 000 and 999
            - If multiple candidates, select the one with highest confidence
            - Format as exactly 3 digits with leading zeros if needed
            - Return ONLY the 3-digit number, nothing else""",
            context=final_synthesis
        )

        return final_answer.strip()