# Workflow ID: limr_17_0
# Benchmark: limr
# Data Indices: [110, 55]

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

        # PHASE 1: META-CLASSIFICATION & DECOMPOSITION
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic decomposition:
            1. Identify the primary mathematical domain (combinatorics, number theory, geometry, algebra, probability).
            2. Detect any hybrid or cross-domain elements.
            3. Assess whether the problem is primarily computational, theoretical, or proof-based.
            4. Determine if exact computation, symbolic manipulation, or combinatorial enumeration is required.
            5. Propose 2-3 distinct high-level solution strategies with their trade-offs.
            6. Output in JSON format with keys: "domain", "hybrid_elements", "solution_strategies", "computational_intensity", "key_constraints".
            """,
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        # Extract strategies for parallel execution
        strategy_analysis = await self.generate(
            instruction=f"""Based on classification:
            {classification}
            
            Generate three distinct solution approaches. For each:
            - Outline the core mathematical insight
            - List required theorems or techniques
            - Identify potential pitfalls or edge cases
            - Estimate confidence level (high/medium/low)
            Format as three clearly separated sections.""",
            context=classification
        )

        # Split into individual strategies for parallel processing
        strategies = strategy_analysis.split("\n\n")
        if len(strategies) < 3:
            # Fallback: generate missing strategies
            missing_count = 3 - len(strategies)
            additional_strategies = await asyncio.gather(*[
                self.generate(
                    instruction=f"Generate additional distinct solution strategy {i+1} for this problem, avoiding overlap with: {strategy_analysis}",
                    context=""
                ) for i in range(missing_count)
            ])
            strategies.extend(additional_strategies)

        # Process each strategy in parallel
        strategy_results = await asyncio.gather(*[
            self.generate(
                instruction=f"""Develop complete solution using this strategy:
                {strategy}
                
                Requirements:
                - Show all mathematical steps
                - Justify each non-trivial assertion
                - Track all variables and constraints
                - Flag any uncertain steps
                - Conclude with numerical answer if possible""",
                context=strategy
            ) for strategy in strategies[:3]
        ])

        # PHASE 3: VALIDATION & REVISION LOOP
        validated_results = []
        for i, result in enumerate(strategy_results):
            # First validation pass
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {result}
                
                Check for:
                1. Logical consistency
                2. Mathematical correctness
                3. Adherence to problem constraints
                4. Edge case coverage
                5. Answer format compliance (integer 000-999)
                
                Output validation report with "PASSED" or "FAILED" at start.""",
                context=result
            )
            
            # Revise if validation fails
            if "FAILED" in validation[:20].upper():
                revised = await self.revise(
                    instruction=f"""Fix all issues identified in validation:
                    {validation}
                    
                    Requirements:
                    - Address every criticism point by point
                    - Maintain mathematical rigor
                    - Preserve correct parts of original solution
                    - Output complete revised solution""",
                    context=result
                )
                # Second validation
                revalidation = await self.generate(
                    instruction=f"""Re-validate revised solution:
                    {revised}
                    
                    Same criteria as before. Output "PASSED" or "FAILED".""",
                    context=revised
                )
                validated_results.append(revised if "PASSED" in revalidation[:20].upper() else "VALIDATION_FAILED")
            else:
                validated_results.append(result)

        # PHASE 4: COMPUTATIONAL VERIFICATION (CONDITIONAL)
        computational_verification = None
        if any("computation" in classification.lower() or "enumerate" in classification.lower() or "probability" in classification.lower()):
            try:
                computational_verification = await self.programmer(
                    instruction=f"""Implement computational solution for this problem:
                    - Use exact arithmetic (no floating point)
                    - Handle edge cases explicitly
                    - Output must be integer between 000-999
                    - Include verification against analytical solution if available
                    
                    Problem context:
                    {self.problem_text}""",
                    context=strategy_results[0],  # Use first strategy as reference
                    max_retries=2
                )
            except Exception:
                computational_verification = "COMPUTATIONAL_FAILED"

        # PHASE 5: ENSEMBLE SYNTHESIS
        all_candidates = [r for r in validated_results if r != "VALIDATION_FAILED"]
        if computational_verification and "FAILED" not in computational_verification:
            all_candidates.append(computational_verification)

        if len(all_candidates) == 0:
            # Emergency fallback
            final_answer = await self.generate(
                instruction="Problem resisted all solution attempts. Make best possible educated guess for integer answer 000-999 based on problem structure and constraints.",
                context=classification
            )
        else:
            final_answer = await self.ensemble(
                instruction="""Synthesize final answer from multiple solution attempts:
                - Prioritize solutions that passed validation
                - Favor computational verification when available and consistent
                - Resolve conflicts by checking against problem constraints
                - If multiple answers remain, select most frequently occurring
                - Final output must be exactly one integer between 000 and 999
                - Justify selection briefly""",
                contexts_list=all_candidates
            )

        # PHASE 6: FINAL VERIFICATION & FORMATTING
        formatted_answer = await self.revise(
            instruction="""Ensure final answer meets all requirements:
            1. Must be exactly one integer between 000 and 999
            2. Must be boxed as \\boxed{answer}
            3. Remove all explanatory text - only the boxed answer remains
            4. If answer is not in correct format, extract the integer and format it properly""",
            context=final_answer
        )

        # Extract just the boxed answer
        answer_extraction = await self.generate(
            instruction=f"""Extract only the final answer from this text:
            {formatted_answer}
            
            Return ONLY the integer inside \\boxed{{}}, nothing else. If no boxed answer, return the most likely integer 000-999.""",
            context=formatted_answer
        )

        return answer_extraction.strip()