# Workflow ID: limr_75_0
# Benchmark: limr
# Data Indices: [343, 36]

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

        # PHASE 1: META-ANALYSIS — Understand problem type and required strategies
        meta_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            1. Primary domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Required solution strategies (proof, computation, optimization, counting, etc.)
            3. Key mathematical objects involved (polynomials, sequences, geometric figures, etc.)
            4. Expected answer format and constraints (integer, range, set of values, etc.)
            5. Potential pitfalls or non-obvious insights needed
            6. Recommended operator sequence for solving
            Present as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION — Break into manageable subproblems
        decomposition = await self.decompose(
            instruction=f"""Based on the meta-analysis:
            {meta_analysis}
            
            Decompose this problem into the minimal set of independent and dependent subproblems.
            For each subproblem:
            - Clearly state what needs to be solved
            - Specify dependencies (which other subproblems must be solved first)
            - Tag with strategy type (compute, prove, count, optimize, etc.)
            - Estimate complexity level (simple, moderate, complex)
            Return as structured list with id, description, dependencies, and tags.""",
            context=meta_analysis
        )

        # PHASE 3: PARALLEL STRATEGY GENERATION — Explore multiple approaches per subproblem
        strategy_tasks = []
        for subproblem in decomposition:
            task = self.generate(
                instruction=f"""For subproblem: {subproblem['description']}
                Generate 3 distinct solution strategies. For each:
                1. Describe the approach in detail
                2. List required mathematical tools or theorems
                3. Estimate success probability and potential failure points
                4. Specify which operator (Generate, Programmer, etc.) is best suited
                Format as numbered list with clear separation between strategies.""",
                context=f"Meta-analysis: {meta_analysis}"
            )
            strategy_tasks.append(task)
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # PHASE 4: CONDITIONAL ROUTING & EXECUTION — Apply appropriate operators
        execution_tasks = []
        for i, (subproblem, strategies) in enumerate(zip(decomposition, strategy_results)):
            # Classify subproblem type for routing
            classification = await self.generate(
                instruction=f"""Classify this subproblem for routing:
                {subproblem['description']}
                
                Choose primary category: [COMPUTATION, PROOF, COUNTING, OPTIMIZATION, STRUCTURAL]
                Justify your choice in one sentence.""",
                context=strategies
            )
            
            if "COMPUTATION" in classification.upper() or "COUNTING" in classification.upper():
                # Route to Programmer for precise calculation
                exec_task = self.programmer(
                    instruction=f"""Implement and execute a precise solution for:
                    {subproblem['description']}
                    
                    Strategies considered:
                    {strategies}
                    
                    Requirements:
                    - Use exact arithmetic (no floating point)
                    - Validate edge cases
                    - Return only the numerical result or set of results
                    - If multiple values, return as comma-separated integers""",
                    context=strategies
                )
            else:
                # Route to Generate for proof/structural reasoning
                exec_task = self.generate(
                    instruction=f"""Develop a complete, rigorous solution for:
                    {subproblem['description']}
                    
                    Selected from these strategies:
                    {strategies}
                    
                    Requirements:
                    - Show all logical steps
                    - Justify non-obvious insights
                    - Verify internal consistency
                    - Extract final answer in required format""",
                    context=strategies
                )
            
            execution_tasks.append(exec_task)
        
        execution_results = await asyncio.gather(*execution_tasks)

        # PHASE 5: ITERATIVE REFINEMENT — Verify and improve each result
        refinement_tasks = []
        for i, (result, subproblem) in enumerate(zip(execution_results, decomposition)):
            refine_task = self.revise(
                instruction=f"""Critically review this solution for subproblem {i+1}:
                {subproblem['description']}
                
                Solution:
                {result}
                
                Verification checklist:
                1. Are all steps mathematically sound?
                2. Are there any calculation errors?
                3. Does it satisfy all problem constraints?
                4. Is the final answer in correct format?
                5. What alternative approaches could confirm this result?
                
                If errors found, provide corrected version. Otherwise, confirm validity.""",
                context=result
            )
            refinement_tasks.append(refine_task)
        
        refined_results = await asyncio.gather(*refinement_tasks)

        # PHASE 6: ENSEMBLE SYNTHESIS — Combine subproblem solutions into final answer
        final_synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into a complete, coherent answer.
            Consider:
            1. How do subproblem results interconnect?
            2. Are there any contradictions between subproblem solutions?
            3. Does the combined solution satisfy all original problem constraints?
            4. Is the final answer format correct (integer or comma-separated integers 000-999)?
            5. What is the confidence level in this final answer?
            
            Resolve any conflicts by selecting the most mathematically rigorous solution.
            Return ONLY the final numerical answer(s) in required format.""",
            contexts_list=refined_results
        )

        # PHASE 7: FINAL EXTRACTION & FORMATTING — Ensure answer meets specifications
        final_answer = await self.revise(
            instruction="""Extract and format the final numerical answer according to problem requirements.
            Rules:
            - Must be integer(s) between 000 and 999
            - If multiple values, separate by commas with no spaces
            - No explanations, no units, no additional text
            - If answer is single digit, pad with leading zeros (e.g., 007)
            - Validate against original problem constraints
            
            Example valid outputs: "42", "123,456,789", "000"
            
            If current output doesn't match this format, correct it.""",
            context=final_synthesis
        )

        # Clean and return final answer
        # Extract only digits and commas, ensure proper formatting
        cleaned = re.sub(r'[^0-9,]', '', final_answer)
        parts = cleaned.split(',')
        formatted_parts = []
        for part in parts:
            if part.isdigit():
                # Ensure 3-digit format for single numbers if needed
                if len(part) == 1:
                    formatted_parts.append(f"00{part}")
                elif len(part) == 2:
                    formatted_parts.append(f"0{part}")
                else:
                    formatted_parts.append(part)
        
        return ','.join(formatted_parts) if formatted_parts else "000"