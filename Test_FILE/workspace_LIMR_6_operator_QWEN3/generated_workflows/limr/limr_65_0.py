# Workflow ID: limr_65_0
# Benchmark: limr
# Data Indices: [78, 254]

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

        # STEP 1: META-ANALYSIS - Understand problem structure and generate solution strategies
        meta_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            1. The mathematical domain (geometry, number theory, combinatorics, algebra, etc.)
            2. Key entities, variables, and constraints
            3. Hidden symmetries, invariants, or special properties
            4. At least 3 distinct solution strategies that could be applicable, with brief rationale for each
            5. Potential pitfalls or common mistakes to avoid
            6. Expected answer format and constraints (e.g., integer between 000-999)
            
            Structure your response clearly with headings for each section. Be exhaustive and precise.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION - Develop multiple solution approaches
        strategy_instructions = [
            """You are a mathematical problem solver specializing in geometric approaches. 
            Using the meta-analysis provided, develop a complete solution strategy using coordinate geometry or synthetic geometry.
            Include: coordinate system setup (if applicable), key theorems to apply, step-by-step reasoning, and final computation plan.
            Assume this is the correct approach and develop it fully.""",
            
            """You are a mathematical problem solver specializing in algebraic and number theoretic approaches.
            Using the meta-analysis provided, develop a complete solution strategy using algebraic manipulation, equations, or number theory.
            Include: variable definitions, equation setup, solution steps, and final computation plan.
            Assume this is the correct approach and develop it fully.""",
            
            """You are a mathematical problem solver specializing in combinatorial and probabilistic approaches.
            Using the meta-analysis provided, develop a complete solution strategy using counting principles, probability, or combinatorial identities.
            Include: case analysis, counting strategy, formula application, and final computation plan.
            Assume this is the correct approach and develop it fully.""",
            
            """You are a mathematical problem solver specializing in trigonometric and vector approaches.
            Using the meta-analysis provided, develop a complete solution strategy using trigonometry, vectors, or complex numbers.
            Include: angle definitions, vector setups, identity applications, and final computation plan.
            Assume this is the correct approach and develop it fully."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=meta_analysis) for instr in strategy_instructions]
        )

        # STEP 3: ADVERSARIAL VALIDATION - Critique each strategy for gaps and feasibility
        critiques = await asyncio.gather(
            *[self.revise(
                instruction="""Critically evaluate this solution strategy. Identify:
                - Any logical gaps or unverified assumptions
                - Computational complexity or potential for error
                - Missing steps or undefined variables
                - Theorems or properties used without proper justification
                - Whether the approach is feasible within reasonable time and precision constraints
                - Alternative interpretations that might invalidate this approach
                
                Be brutally honest. If the approach is fundamentally flawed, say so explicitly.""",
                context=strat
            ) for strat in strategy_attempts]
        )

        # STEP 4: SYNTHESIS - Combine the best elements into a unified solution plan
        unified_plan = await self.ensemble(
            instruction="""You are a senior mathematics competition coach reviewing multiple solution attempts.
            Synthesize the strongest elements from each approach into a single, robust, and elegant solution plan.
            Consider:
            - Which approach has the fewest assumptions and highest reliability?
            - Which approach minimizes computational complexity and maximizes precision?
            - Can elements from different approaches be combined for a better solution?
            - What is the most direct path to the required answer format (integer 000-999)?
            
            Produce a step-by-step solution plan that a skilled mathematician could follow to solve the problem correctly.
            Include clear mathematical reasoning and justification for each step.""",
            contexts_list=[f"Strategy: {s}\n\nCritique: {c}" for s, c in zip(strategy_attempts, critiques)]
        )

        # STEP 5: HIERARCHICAL DECOMPOSITION - Break the unified plan into atomic subproblems
        decomposition = await self.decompose(
            instruction="""Break down the unified solution plan into atomic, executable subproblems.
            Each subproblem should:
            - Be self-contained and solvable independently (given its dependencies)
            - Have a clear mathematical objective
            - Specify required inputs and expected outputs
            - Include validation criteria (how to check if the subproblem was solved correctly)
            - Have minimal computational complexity
            
            Order subproblems by dependency. The final subproblem should produce the answer in the required format (integer 000-999).""",
            context=unified_plan
        )

        # STEP 6: EXECUTE SUBPROBLEMS - Solve each subproblem with targeted computation
        subproblem_results = {}
        # Sort by dependencies (simple topological sort for linear dependencies)
        sorted_subproblems = sorted(decomposition, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0)
        
        for subproblem in sorted_subproblems:
            sub_id = subproblem['id']
            deps = [dep.strip() for dep in subproblem.get('dependencies', '').split(',') if dep.strip()]
            
            # Build context from completed dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {subproblem_results[dep]}" for dep in deps if dep in subproblem_results])
            
            full_context = f"Subproblem Description: {subproblem['description']}\n\nDependencies:\n{dep_context}"
            
            # Execute with programmer for computational subproblems, generate for reasoning subproblems
            if any(keyword in subproblem['description'].lower() for keyword in ['compute', 'calculate', 'find the value', 'determine']):
                result = await self.programmer(
                    instruction=f"""Solve this mathematical subproblem precisely:
                    {subproblem['description']}
                    
                    Validation criteria: {subproblem.get('validation', 'Result should be mathematically consistent with problem constraints')}
                    
                    Use exact arithmetic. Return only the final result as a number or simple expression.
                    If multiple steps are needed, show them clearly but concisely.""",
                    context=full_context,
                    max_retries=3
                )
            else:
                result = await self.generate(
                    instruction=f"""Solve this mathematical subproblem through reasoning:
                    {subproblem['description']}
                    
                    Provide a clear, step-by-step mathematical argument leading to the solution.
                    Validation criteria: {subproblem.get('validation', 'Reasoning should be logically sound and complete')}""",
                    context=full_context
                )
            
            subproblem_results[sub_id] = result

        # STEP 7: FINAL VERIFICATION - Validate the complete solution against original problem
        final_answer = subproblem_results.get(sorted_subproblems[-1]['id'], "") if sorted_subproblems else ""
        
        verification = await self.generate(
            instruction=f"""Verify the final answer against the original problem:
            Final Answer: {final_answer}
            
            Check:
            1. Does it satisfy all constraints in the original problem?
            2. Is it in the required format (integer between 000 and 999)?
            3. Are there any mathematical inconsistencies?
            4. Could there be alternative interpretations that would change the answer?
            
            If verification fails, propose corrections or indicate which subproblem needs re-evaluation.
            If verification passes, output ONLY the final integer answer in the format: ###ANSWER: XXX""",
            context=f"Original Solution Plan:\n{unified_plan}\n\nSubproblem Results:\n{json.dumps(subproblem_results, indent=2)}"
        )

        # Extract final answer
        if "###ANSWER:" in verification:
            final_output = verification.split("###ANSWER:")[1].split()[0].strip()
        else:
            # Fallback: try to extract any 3-digit number
            import re
            numbers = re.findall(r'\b\d{3}\b', verification)
            final_output = numbers[0] if numbers else "000"

        return final_output