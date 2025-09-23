# Workflow ID: mgsmbn_110_0
# Benchmark: mgsmbn
# Data Indices: [26, 157]

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

        # Step 1: Generate multiple problem interpretations in parallel
        interpretations = await asyncio.gather(
            self.generate(
                instruction="""Analyze this Bengali math problem from a mathematical modeling perspective.
                Identify:
                - All named entities (people, objects, places)
                - All numerical values and their associated units or meanings
                - All relational phrases (e.g., 'more than', 'less than', 'half of')
                - The target unknown to solve for
                - Any implicit constraints (e.g., non-negative counts, integer requirements)
                Format as a structured JSON-like outline.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this Bengali math problem from a narrative timeline perspective.
                Reconstruct the sequence of events or states described.
                Identify:
                - Temporal order of operations (what happens first, next, last)
                - State changes (e.g., 'initial amount', 'after adding', 'final count')
                - Cause-effect relationships
                - Any hidden steps implied by context
                Format as a chronological step-by-step breakdown.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this Bengali math problem from an entity-relationship graph perspective.
                Map:
                - Entities as nodes
                - Quantitative relationships as directed edges with formulas
                - Dependencies between unknowns
                - Cycles or contradictions in relationships
                Represent as a dependency graph description with equations.""",
                context=""
            )
        )

        # Step 2: Ensemble interpretations into unified problem representation
        unified_analysis = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a single coherent problem representation.
            Prioritize:
            1. Mathematical consistency (equations must be solvable)
            2. Narrative plausibility (timeline must make sense)
            3. Entity relationship integrity (no contradictory dependencies)
            Resolve conflicts by favoring the most mathematically precise interpretation.
            Output a consolidated problem specification with:
            - Known values
            - Unknowns to solve for
            - System of equations or step-by-step procedure
            - Validation constraints""",
            contexts_list=interpretations
        )

        # Step 3: Classify problem complexity to determine solution path
        complexity_analysis = await self.generate(
            instruction=f"""Classify the problem based on the unified analysis:
            {unified_analysis}

            Categorize as one of:
            A. DIRECT_ARITHMETIC: Single-step calculation with explicit numbers
            B. SEQUENTIAL: Multiple steps but no variables or algebra
            C. SINGLE_VARIABLE: Requires solving for one unknown with simple algebra
            D. MULTI_VARIABLE: System of equations with multiple unknowns
            E. CONSTRAINT_HEAVY: Requires checking real-world constraints after calculation

            Also estimate confidence level (HIGH/MEDIUM/LOW) based on clarity of relationships.
            Output format: "CATEGORY: [type], CONFIDENCE: [level], JUSTIFICATION: [brief reason]".""",
            context=unified_analysis
        )

        # Step 4: Conditional branching based on complexity
        category = "SEQUENTIAL"  # default
        confidence = "MEDIUM"
        
        if "CATEGORY:" in complexity_analysis:
            lines = complexity_analysis.split('\n')
            for line in lines:
                if line.startswith("CATEGORY:"):
                    category = line.split("CATEGORY:")[1].split(",")[0].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence = line.split("CONFIDENCE:")[1].split(",")[0].strip()

        # Step 5: Solve based on category
        if category in ["DIRECT_ARITHMETIC", "SEQUENTIAL"] and confidence == "HIGH":
            # Simple path: go straight to programmer
            solution_attempt = await self.programmer(
                instruction=f"""Solve this problem directly using the unified analysis:
                {unified_analysis}
                
                Requirements:
                - Show all calculation steps
                - Verify unit consistency
                - Output only the final numerical answer
                - If any step produces invalid result (negative count, fraction where inappropriate), flag error""",
                context=unified_analysis
            )
        else:
            # Complex path: decompose and solve step by step
            decomposition = await self.decompose(
                instruction=f"""Break down this problem into minimal solvable subproblems:
                {unified_analysis}
                
                Guidelines:
                - Each subproblem should be independently solvable with given information
                - Order subproblems by dependency (prerequisites first)
                - Include validation checks as separate subproblems where appropriate
                - Maximum 5 subproblems for efficiency
                - Format each as: ID: [number], Description: [what to solve], Dependencies: [IDs]""",
                context=unified_analysis
            )

            # Solve subproblems sequentially respecting dependencies
            subproblem_results = {}
            for subproblem in decomposition:
                sub_id = subproblem['id']
                deps = subproblem['dependencies'].split(',') if subproblem['dependencies'] else []
                
                # Wait for dependencies
                dep_context = "\n".join([f"Subproblem {did}: {subproblem_results.get(did, 'PENDING')}" 
                                       for did in deps if did in subproblem_results])
                
                # Construct context for this subproblem
                full_context = f"""UNIFIED ANALYSIS:
                {unified_analysis}

                DEPENDENCY RESULTS:
                {dep_context}

                CURRENT SUBPROBLEM:
                {subproblem['description']}"""
                
                # Solve subproblem
                sub_result = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context:
                    {full_context}
                    
                    Requirements:
                    - Show calculation steps
                    - Validate against constraints
                    - Output only the numerical result or 'ERROR: [reason]' if unsolvable""",
                    context=full_context
                )
                subproblem_results[sub_id] = sub_result

            # Extract final answer from last subproblem
            last_sub_id = decomposition[-1]['id']
            solution_attempt = subproblem_results.get(last_sub_id, "ERROR: No solution generated")

        # Step 6: Validate and revise solution
        validated_solution = await self.revise(
            instruction=f"""Critically validate this solution:
            {solution_attempt}
            
            Against original problem and unified analysis:
            {unified_analysis}
            
            Check:
            1. Mathematical correctness of each step
            2. Unit consistency throughout
            3. Real-world plausibility (no negative people, fractional children unless specified)
            4. Matches target unknown requested in problem
            5. No calculation errors
            
            If any issue found, correct it and explain the fix.
            If no issues, output the final numerical answer only.""",
            context=solution_attempt
        )

        # Step 7: Final sanity check and extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from this validated solution:
            {validated_solution}
            
            Also perform final sanity check:
            - Does this answer make sense in the context of the original Bengali problem?
            - Is it within reasonable bounds? (e.g., not millions when problem is about classroom items)
            - Does it satisfy all constraints mentioned in the problem?
            
            If answer passes all checks, output ONLY the number (integer or decimal).
            If any doubt remains, output 'RETRY_REQUIRED'.""",
            context=validated_solution
        )

        # Step 8: Handle edge case where retry is needed
        if "RETRY_REQUIRED" in final_answer or "ERROR" in final_answer.upper():
            # Fallback: try direct extraction from original interpretations
            backup_answer = await self.ensemble(
                instruction="""From the multiple initial interpretations, extract the most consistent numerical answer.
                Prioritize answers that:
                - Appear in multiple interpretations
                - Satisfy basic arithmetic checks
                - Match the problem's expected scale
                Output only the number.""",
                contexts_list=interpretations
            )
            return backup_answer.strip()
        
        return final_answer.strip()