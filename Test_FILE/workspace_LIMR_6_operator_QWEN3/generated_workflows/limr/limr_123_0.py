# Workflow ID: limr_123_0
# Benchmark: limr
# Data Indices: [61, 119]

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

        # PHASE 1: DECOMPOSE THE PROBLEM INTO SUBPROBLEMS
        decomposition = await self.decompose(
            instruction="""Break this mathematical competition problem into logically independent subproblems.
            Each subproblem should be solvable in sequence or parallel, with clear dependencies.
            Focus on:
            - Identifying key mathematical objects (variables, constraints, expressions)
            - Recognizing required theorems or techniques (AM-GM, induction, coordinate geometry, etc.)
            - Separating simplification, transformation, computation, and verification steps
            - Flagging steps that may have multiple valid approaches
            Output as structured subproblems with dependencies.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION FOR AMBIGUOUS STEPS
        strategy_tasks = []
        subproblem_contexts = {}

        for subproblem in decomposition:
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            deps = subproblem.get('dependencies', "").split(',') if subproblem.get('dependencies') else []

            # Wait for dependencies (simplified: we assume topological order in decomposition list)
            dep_context = "\n".join([subproblem_contexts.get(dep_id.strip(), "") for dep_id in deps if dep_id.strip()])

            # For high-risk or strategy-heavy steps, generate multiple approaches
            if any(keyword in sp_desc.lower() for keyword in ["minimize", "maximize", "prove", "find all", "how many"]):
                # Generate 3 parallel strategies
                strategies = await asyncio.gather(
                    self.generate(
                        instruction=f"""Develop Strategy A for subproblem: {sp_desc}
                        Use algebraic manipulation and standard inequalities (AM-GM, Cauchy-Schwarz).
                        Show step-by-step reasoning. Assume dependencies: {dep_context}""",
                        context=dep_context
                    ),
                    self.generate(
                        instruction=f"""Develop Strategy B for subproblem: {sp_desc}
                        Use calculus or Lagrange multipliers if applicable.
                        Show step-by-step reasoning. Assume dependencies: {dep_context}""",
                        context=dep_context
                    ),
                    self.generate(
                        instruction=f"""Develop Strategy C for subproblem: {sp_desc}
                        Use substitution, symmetry, or combinatorial argument.
                        Show step-by-step reasoning. Assume dependencies: {dep_context}""",
                        context=dep_context
                    )
                )
                
                # Ensemble to select or synthesize best strategy
                chosen_strategy = await self.ensemble(
                    instruction=f"""Evaluate these 3 strategies for subproblem: {sp_desc}
                    Criteria:
                    1. Mathematical correctness and rigor
                    2. Computational feasibility
                    3. Elegance and insight
                    4. Alignment with dependencies: {dep_context}
                    Select the single best strategy OR synthesize a hybrid approach.
                    Output only the selected/synthesized strategy with clear steps.""",
                    contexts_list=strategies
                )
                subproblem_contexts[sp_id] = chosen_strategy
            else:
                # Direct solution for straightforward steps
                solution = await self.generate(
                    instruction=f"""Solve subproblem: {sp_desc}
                    Show all steps. Use dependencies: {dep_context}
                    Be precise and rigorous. Output only the solution and key insights.""",
                    context=dep_context
                )
                # Revise for error-checking
                revised = await self.revise(
                    instruction="""Critically review this solution:
                    - Check for algebraic errors
                    - Verify constraint satisfaction
                    - Ensure logical flow
                    - Confirm answer format (if final answer, must be integer 000-999)
                    Output corrected version with fixes marked.""",
                    context=solution
                )
                subproblem_contexts[sp_id] = revised

        # PHASE 3: SYNTHESIZE FULL SOLUTION
        full_solution_draft = "\n\n".join([
            f"Subproblem {sp['id']}: {sp['description']}\nSolution: {subproblem_contexts.get(sp['id'], 'PENDING')}"
            for sp in decomposition
        ])

        synthesized = await self.generate(
            instruction="""Synthesize all subproblem solutions into a coherent, end-to-end proof or derivation.
            Structure:
            1. Restate the original problem
            2. Outline the solution strategy
            3. Present the logical flow with subproblem results integrated
            4. Conclude with the final answer
            Ensure mathematical rigor and clarity. Highlight key insights.""",
            context=full_solution_draft
        )

        # PHASE 4: VERIFICATION & REFINEMENT LOOP
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction="""Act as a ruthless mathematical critic. Verify this solution:
                - Is every step logically justified?
                - Are all constraints respected?
                - Is the final answer an integer between 000 and 999?
                - Are there any calculation errors?
                If perfect, output 'VERIFIED'. Otherwise, list all errors concisely.""",
                context=synthesized
            )
            
            if "VERIFIED" in validation.upper() and "ERROR" not in validation.upper():
                break
            else:
                synthesized = await self.revise(
                    instruction=f"""Fix all errors identified in validation:
                    {validation}
                    Preserve correct parts. Improve clarity and rigor.
                    Ensure final answer is boxed as \\boxed{{000}} format.""",
                    context=synthesized
                )

        # PHASE 5: COMPUTATIONAL VERIFICATION (IF APPLICABLE)
        # Check if problem involves numerical computation
        if any(term in self.problem_text.lower() for term in ["compute", "calculate", "value", "minimum", "maximum", "sum"]):
            code_verification = await asyncio.gather(
                self.programmer(
                    instruction="""Generate Python code to numerically verify the final answer.
                    Use sympy for symbolic math or numpy for numerical methods.
                    Code must:
                    - Reproduce the problem constraints
                    - Implement the derived solution
                    - Output only the final integer answer (000-999)
                    - Include assertions for validation""",
                    context=synthesized
                ),
                self.programmer(
                    instruction="""Generate ALTERNATIVE Python code using a different method (e.g., brute-force search, Monte Carlo, different algorithm).
                    Must output same format: final integer answer.
                    Include bounds checking and error handling.""",
                    context=synthesized
                )
            )
            
            # Ensemble code outputs
            code_result = await self.ensemble(
                instruction="""Compare two computational verifications:
                - Do they agree on the final integer answer?
                - If yes, output the answer.
                - If no, identify discrepancy and suggest resolution.
                Final output must be a single integer in 000-999 format.""",
                contexts_list=code_verification
            )
            
            # Extract integer from code result
            match = re.search(r'\b\d{1,3}\b', code_result)
            if match:
                final_answer = int(match.group())
                if 0 <= final_answer <= 999:
                    return f"{final_answer:03d}"

        # PHASE 6: FINAL ANSWER EXTRACTION (Fallback)
        final_extraction = await self.generate(
            instruction="""Extract the final answer from the solution.
            The answer must be an integer between 000 and 999.
            If multiple candidates exist, choose the most rigorously derived.
            If no clear answer, return 000.
            Output ONLY the 3-digit number with leading zeros if needed.""",
            context=synthesized
        )
        
        # Clean and format
        match = re.search(r'\b\d{1,3}\b', final_extraction)
        if match:
            answer = int(match.group())
            if 0 <= answer <= 999:
                return f"{answer:03d}"
        
        # Ultimate fallback
        return "000"