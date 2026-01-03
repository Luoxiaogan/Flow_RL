# Workflow ID: limr_89_0
# Benchmark: limr
# Data Indices: [179, 13]

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

        # STEP 1: CLASSIFY PROBLEM & SELECT STRATEGIES
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Output in JSON format with keys:
            - "problem_type": One of ["algebra", "number_theory", "combinatorics", "geometry", "optimization", "sequences", "other"]
            - "required_techniques": List of specific mathematical techniques needed (e.g., "polynomial expansion", "prime factorization", "inclusion-exclusion")
            - "decomposable": Boolean indicating if problem can be broken into sequential subproblems
            - "verification_approach": Suggested method to computationally verify answer (e.g., "expand polynomial", "enumerate divisors", "simulate cases")
            - "potential_pitfalls": List of common errors or tricky aspects to watch for
            Be precise and justify each classification decision based on problem structure.""",
            context=""
        )

        try:
            class_data = json.loads(classification)
        except:
            # Fallback classification if JSON fails
            class_data = {
                "problem_type": "algebra",
                "required_techniques": ["symbolic manipulation"],
                "decomposable": False,
                "verification_approach": "symbolic computation",
                "potential_pitfalls": ["sign errors", "missing terms"]
            }

        # STEP 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = {
            "algebra": """Solve using algebraic manipulation. Expand expressions step by step. Track coefficients carefully. Show all intermediate products. Justify each algebraic step with mathematical rules.""",
            "number_theory": """Solve using number theory principles. Factorize all numbers into primes. Apply LCM/GCD properties. Consider divisibility conditions. Enumerate possible cases systematically.""",
            "combinatorics": """Solve using combinatorial reasoning. Identify what is being counted. Apply counting principles (multiplication, addition, inclusion-exclusion). Consider symmetries and overcounting. Verify with small cases.""",
            "geometry": """Solve using geometric principles. Assign coordinates if helpful. Use vector operations or trigonometric identities. Apply geometric theorems explicitly. Show all distance/angle calculations.""",
            "optimization": """Solve by finding extrema. Use calculus if applicable (derivatives, critical points). Consider boundary cases. Apply inequalities (AM-GM, Cauchy-Schwarz). Verify global vs local optima.""",
            "sequences": """Solve using sequence properties. Find recurrence relations. Use generating functions or characteristic equations. Compute initial terms to detect patterns. Prove by induction if needed."""
        }

        # Generate 3 parallel solution attempts
        base_strategy = class_data["problem_type"]
        fallback_strategies = [s for s in strategy_instructions.keys() if s != base_strategy][:2]
        selected_strategies = [base_strategy] + fallback_strategies

        strategy_tasks = []
        for i, strategy_type in enumerate(selected_strategies):
            instruction = f"""STRATEGY {i+1} ({strategy_type.upper()} APPROACH):
            {strategy_instructions.get(strategy_type, 'Apply general mathematical reasoning.')}
            
            Additional context from classification:
            - Required techniques: {', '.join(class_data.get('required_techniques', []))}
            - Potential pitfalls: {', '.join(class_data.get('potential_pitfalls', []))}
            
            Provide a complete, step-by-step solution. Box your final answer as \\boxed{{answer}}."""
            
            strategy_tasks.append(self.generate(instruction=instruction, context=""))

        # STEP 3: CONDITIONAL DECOMPOSITION (if needed)
        decomposition_result = None
        if class_data.get("decomposable", False):
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, sequentially dependent subproblems. 
                Each subproblem should:
                - Be solvable in isolation
                - Have clearly defined inputs and outputs
                - Not assume knowledge beyond its dependencies
                - Contribute directly to the final solution
                Format each subproblem with clear mathematical objectives.""",
                context=""
            )
            
            # Solve subproblems in dependency order
            solved_subproblems = {}
            for subproblem in decomposition:
                deps_context = "\n".join([f"Subproblem {dep}: {solved_subproblems.get(dep, '')}" 
                                        for dep in subproblem.get('dependencies', '').split(',') if dep.strip()])
                
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Based on these solved dependencies:
                    {deps_context}
                    
                    Show all work and justify each step mathematically.""",
                    context=deps_context
                )
                
                # Revise for rigor
                revised_sub = await self.revise(
                    instruction="Improve mathematical rigor. Add missing justifications. Verify calculations. Ensure notation is precise.",
                    context=sub_solution
                )
                
                solved_subproblems[subproblem['id']] = revised_sub
            
            # Synthesize subproblem solutions
            decomposition_result = await self.generate(
                instruction=f"""Synthesize all subproblem solutions into a complete answer:
                {json.dumps(solved_subproblems, indent=2)}
                
                Ensure logical flow between subproblems. State the final answer clearly.""",
                context=json.dumps(solved_subproblems)
            )

        # Gather all strategy results (including decomposition if applicable)
        strategy_results = await asyncio.gather(*strategy_tasks)
        all_candidates = list(strategy_results)
        if decomposition_result:
            all_candidates.append(decomposition_result)

        # STEP 4: ENSEMBLE SYNTHESIS
        final_synthesis = await self.ensemble(
            instruction=f"""Synthesize the most correct and rigorous solution from these candidates:
            - Compare mathematical approaches and identify points of agreement/disagreement
            - Trace discrepancies to specific steps or assumptions
            - Select the solution with the most complete justification and fewest logical gaps
            - If multiple solutions agree, combine their strongest elements
            - Final answer must be an integer between 000 and 999, boxed as \\boxed{{answer}}
            
            Classification context: {json.dumps(class_data, indent=2)}""",
            contexts_list=all_candidates
        )

        # STEP 5: COMPUTATIONAL VERIFICATION
        verification_code = await self.programmer(
            instruction=f"""Write Python code to verify the proposed answer: {final_synthesis}
            
            Verification approach: {class_data.get('verification_approach', 'symbolic computation')}
            
            Requirements:
            - Code must be self-contained and executable
            - Must output 'Verified' if answer is correct, 'Error: [reason]' if incorrect
            - For algebraic problems: expand expressions and extract coefficients
            - For number theory: validate LCM/GCD conditions with actual computation
            - For combinatorics: enumerate cases for small inputs to verify logic
            - Include detailed comments explaining verification logic""",
            context=final_synthesis
        )

        # STEP 6: ITERATIVE REFINEMENT (if verification fails)
        current_answer = final_synthesis
        for iteration in range(3):  # Max 3 refinement loops
            if "Verified" in verification_code:
                break
                
            # Revise based on verification feedback
            revised_answer = await self.revise(
                instruction=f"""The following solution failed verification:
                {verification_code}
                
                Identify the exact step where the error occurred. Was it:
                - Algebraic manipulation error?
                - Misapplied theorem or formula?
                - Counting/combination mistake?
                - Arithmetic calculation error?
                - Logical flaw in reasoning?
                
                Correct the error and provide a revised solution with explicit justification for each step.
                Ensure final answer is an integer between 000 and 999, boxed as \\boxed{{answer}}.""",
                context=current_answer
            )
            
            # Re-verify
            verification_code = await self.programmer(
                instruction=f"""Verify this revised answer: {revised_answer}
                
                Verification approach: {class_data.get('verification_approach', 'symbolic computation')}
                
                Same requirements as before: output 'Verified' or 'Error: [reason]'""",
                context=revised_answer
            )
            
            current_answer = revised_answer

        # FINAL OUTPUT
        return current_answer if "Verified" in verification_code else final_synthesis