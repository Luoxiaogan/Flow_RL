# Workflow ID: limr_128_0
# Benchmark: limr
# Data Indices: [96, 194]

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

        # STEP 1: Generate Problem DNA Profile (Parallel Classification)
        classification_instructions = [
            """Analyze the problem and classify its mathematical nature. Answer:
            - Primary domain (algebra, geometry, combinatorics, number theory, optimization, sequences)
            - Key techniques likely needed (e.g., AM-GM, modular arithmetic, coordinate geometry)
            - Expected solution structure (proof, computation, construction)
            - Hidden symmetries or invariants
            - Answer format expectations (integer, expression, etc.)
            Be concise but comprehensive.""",
            
            """Identify all mathematical objects and their relationships:
            - Variables, constants, functions
            - Constraints and boundary conditions
            - Objective (minimize, maximize, count, prove)
            - Special properties (symmetry, periodicity, monotonicity)
            Structure as bullet points.""",
            
            """Predict solution difficulty and potential pitfalls:
            - Likely computational bottlenecks
            - Common misinterpretations
            - Non-obvious transformations needed
            - Theorems or identities that might unlock the solution
            Prioritize insights that guide strategy selection."""
        ]

        classifications = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in classification_instructions]
        )
        
        # Synthesize classifications into unified Problem DNA
        problem_dna = await self.ensemble(
            instruction="""Synthesize these three classifications into a unified Problem DNA Profile.
            Resolve contradictions by prioritizing specificity and mathematical rigor.
            Output must include:
            - Dominant mathematical domain
            - Recommended primary solution strategy
            - Backup strategy if primary fails
            - Computational complexity estimate (low/medium/high)
            - Key variables and constraints to track
            Format as structured JSON-like text.""",
            contexts_list=classifications
        )

        # STEP 2: Conditional Strategy Selection
        strategy_branch = await self.generate(
            instruction=f"""Based on this Problem DNA:
            {problem_dna}
            
            Select the optimal solution architecture:
            A) If optimization + symmetry detected → Use substitution + inequality path
            B) If recursive + modular → Use generating functions + modular reduction
            C) If geometric + distance → Use coordinate system + vector calculus
            D) If combinatorial + counting → Use inclusion-exclusion or bijection
            E) If algebraic + functional → Use substitution + polynomial factorization
            
            Also, ALWAYS prepare a lateral strategy (different from primary) as backup.
            
            Output format:
            Primary Strategy: [A-E]
            Lateral Strategy: [A-E different from primary]
            Decomposition Blueprint: [brief outline of subproblems]""",
            context=problem_dna
        )

        # STEP 3: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Decompose the problem using this strategy:
            {strategy_branch}
            
            Create 3-7 subproblems with clear dependencies.
            Each subproblem must be solvable independently once dependencies are met.
            Include:
            - Mathematical objective of subproblem
            - Required inputs from other subproblems
            - Expected output format
            - Validation criteria for correctness""",
            context=strategy_branch
        )

        # Summarize decomposition for context management
        decomposition_summary = await self.summarize(
            instruction="""Condense this decomposition into a dependency graph summary.
            List subproblems by ID, their purpose, and prerequisites.
            Omit implementation details — focus on structure and flow.
            This will guide parallel execution.""",
            context=str(decomposition)
        )

        # STEP 4: Parallel Subproblem Solving
        async def solve_subproblem(sub):
            sub_id = sub['id']
            sub_desc = sub['description']
            deps = sub.get('dependencies', "")
            
            # Generate initial solution attempt
            solution = await self.generate(
                instruction=f"""Solve subproblem {sub_id}: {sub_desc}
                Dependencies: {deps}
                Follow the strategy outlined in the Problem DNA.
                Show all steps. If stuck, propose alternative approaches.
                Output must include final answer for this subproblem and reasoning.""",
                context=decomposition_summary
            )
            
            # Validate and revise up to 2 times
            for attempt in range(2):
                validation = await self.generate(
                    instruction=f"""Critique this solution for subproblem {sub_id}:
                    - Check for logical gaps
                    - Verify algebraic manipulations
                    - Ensure dependencies are properly used
                    - Flag any assumptions not justified
                    If no issues, output 'VALID'. Otherwise, list specific errors.""",
                    context=solution
                )
                
                if "VALID" in validation.upper():
                    break
                    
                solution = await self.revise(
                    instruction=f"""Revise based on critique:
                    {validation}
                    Fix all identified issues. Maintain mathematical rigor.
                    If original approach is flawed, pivot to lateral strategy from Problem DNA.""",
                    context=solution
                )
            else:
                # After 2 revisions, try lateral approach
                solution = await self.generate(
                    instruction=f"""Original approach failed. Apply lateral strategy from Problem DNA:
                    {strategy_branch}
                    Solve subproblem {sub_id}: {sub_desc}
                    Start fresh with new perspective.""",
                    context=decomposition_summary
                )
            
            return solution

        # Execute subproblems in dependency order (simplified: assume topological sort)
        subproblem_solutions = {}
        for sub in decomposition:
            solution = await solve_subproblem(sub)
            subproblem_solutions[sub['id']] = solution

        # STEP 5: Synthesize Final Solution
        synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in subproblem_solutions.items()])
        
        final_solution = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into complete answer.
            Integrate results following dependency graph.
            Ensure global consistency and satisfy all original constraints.
            Derive final numerical answer (integer 000-999).
            Show how subproblem results combine to final answer.""",
            context=synthesis_context
        )

        # STEP 6: Computational Verification (if needed)
        needs_computation = await self.generate(
            instruction="""Does the final solution require computational verification?
            (e.g., large summation, equation solving, numerical optimization)
            If yes, describe the exact computation needed.
            If no, output 'NONE'.""",
            context=final_solution
        )
        
        if "NONE" not in needs_computation.upper():
            computed_result = await self.programmer(
                instruction=f"""Execute this computation:
                {needs_computation}
                Return ONLY the integer result (000-999 format).
                Use exact arithmetic. No floating point approximations.""",
                context=final_solution,
                max_retries=3
            )
            final_solution = f"{final_solution}\n\nCOMPUTED VERIFICATION: {computed_result}"

        # STEP 7: Answer Extraction and Formatting
        formatted_answer = await self.revise(
            instruction="""Extract the final integer answer from 000 to 999.
            Remove all reasoning, units, variables — keep only the 3-digit integer.
            If answer is single or double digit, pad with leading zeros.
            If multiple candidates, select the one consistent with all constraints.
            If no valid integer found, output '000' and flag for review.""",
            context=final_solution
        )

        # Final validation: ensure it's a 3-digit integer
        match = re.search(r'\b(\d{3})\b', formatted_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any integer and format
            numbers = re.findall(r'\d+', formatted_answer)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"{num:03d}"
            else:
                return "000"