# Workflow ID: limr_91_0
# Benchmark: limr
# Data Indices: [202, 253]

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
        
        # PHASE 1: Deep Problem Analysis & Classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive mathematical autopsy of this problem:
            1. Identify the core mathematical domain (geometry, number theory, combinatorics, algebra, etc.)
            2. Extract all variables, constraints, and boundary conditions
            3. Determine the answer format (integer 000-999, fraction, etc.)
            4. List known mathematical principles that might apply
            5. Flag any potential edge cases or degenerate scenarios
            6. Estimate computational complexity (brute force feasible? analytical solution needed?)
            7. Propose 2-3 high-level solution strategies
            Structure your response with clear section headers.""",
            context=""
        )
        
        # PHASE 2: Strategic Decomposition
        decomposition = await self.decompose(
            instruction="""Break this problem into interdependent subproblems:
            - Each subproblem should be mathematically atomic (solvable with one technique)
            - Explicitly state dependencies between subproblems
            - Include verification steps for each subproblem
            - Flag any subproblems that require creative insight vs. mechanical computation
            Use the problem analysis above to guide your decomposition.""",
            context=problem_analysis
        )
        
        # PHASE 3: Parallel Solution Exploration
        # Group subproblems by type: computational vs conceptual
        computational_tasks = []
        conceptual_tasks = []
        
        for subproblem in decomposition:
            if any(keyword in subproblem['description'].lower() for keyword in ['calculate', 'compute', 'count', 'enumerate', 'solve equation']):
                computational_tasks.append(subproblem)
            else:
                conceptual_tasks.append(subproblem)
        
        # Solve computational subproblems with Programmer
        computational_results = []
        if computational_tasks:
            computational_results = await asyncio.gather(*[
                self.programmer(
                    instruction=f"""Solve this subproblem with mathematical precision:
                    {task['description']}
                    
                    Constraints from problem analysis:
                    {problem_analysis}
                    
                    Requirements:
                    - Show all steps
                    - Handle edge cases explicitly
                    - Return final answer as integer 000-999 if applicable
                    - If answer is fractional, reduce to lowest terms""",
                    context=problem_analysis,
                    max_retries=3
                ) for task in computational_tasks
            ])
        
        # Solve conceptual subproblems with Generate + Revise
        conceptual_results = []
        if conceptual_tasks:
            conceptual_solutions = await asyncio.gather(*[
                self.generate(
                    instruction=f"""Derive the mathematical insight needed for:
                    {task['description']}
                    
                    Use formal notation and rigorous reasoning.
                    Reference relevant theorems or identities.
                    Structure as: Theorem/Principle → Application → Conclusion""",
                    context=problem_analysis
                ) for task in conceptual_tasks
            ])
            
            # Refine conceptual solutions
            conceptual_results = await asyncio.gather(*[
                self.revise(
                    instruction="""Improve this mathematical derivation:
                    - Fill any logical gaps
                    - Add missing edge case analysis
                    - Ensure notation is precise and consistent
                    - Cross-validate with problem constraints""",
                    context=solution
                ) for solution in conceptual_solutions
            ])
        
        # PHASE 4: Synthesis & Creative Reformulation (if needed)
        all_results = computational_results + conceptual_results
        synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into a complete answer:
            1. Resolve dependencies between subproblems
            2. Combine computational results with conceptual insights
            3. Verify consistency across all components
            4. If synthesis fails, propose one radical reformulation of the entire problem
               (change of variables, geometric reinterpretation, generating function, etc.)
            5. Output final answer as integer 000-999 with supporting reasoning""",
            contexts_list=all_results
        )
        
        # PHASE 5: Adversarial Verification Loop
        current_solution = synthesis
        for iteration in range(3):  # Max 3 verification cycles
            verification = await self.generate(
                instruction=f"""Play devil's advocate: Find the flaw in this solution:
                {current_solution}
                
                Attack it from these angles:
                - Mathematical rigor (is every step justified?)
                - Edge cases (did you miss boundary conditions?)
                - Computational accuracy (are calculations correct?)
                - Answer format (is it integer 000-999?)
                
                If no flaw found, respond 'VERIFIED'.
                If flaw found, describe it precisely.""",
                context=current_solution
            )
            
            if "VERIFIED" in verification.upper():
                break
            else:
                # Fix the flaw and resynthesize
                current_solution = await self.revise(
                    instruction=f"""Fix the following flaw:
                    {verification}
                    
                    Preserve correct parts of original solution.
                    Add missing rigor or calculations.
                    Ensure final answer is integer 000-999.""",
                    context=current_solution
                )
                
                # Quick resynthesis
                current_solution = await self.ensemble(
                    instruction="Incorporate the fix while preserving correct elements. Output final integer answer.",
                    contexts_list=[current_solution]
                )
        
        # PHASE 6: Final Answer Extraction & Formatting
        final_answer = await self.programmer(
            instruction="""Extract the final integer answer from this solution:
            - Must be between 000 and 999
            - If solution contains multiple candidates, select the correct one based on problem constraints
            - If answer is fractional, convert appropriately (floor/ceiling as context demands)
            - If no valid answer found, return 000
            - Output ONLY the 3-digit integer, nothing else""",
            context=current_solution,
            max_retries=2
        )
        
        # Clean and validate final answer
        answer_match = re.search(r'\b\d{1,3}\b', final_answer)
        if answer_match:
            answer = int(answer_match.group())
            return f"{answer:03d}"  # Ensure 3-digit format
        else:
            return "000"  # Fallback for extraction failures