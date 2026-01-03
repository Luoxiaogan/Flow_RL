# Workflow ID: limr_111_0
# Benchmark: limr
# Data Indices: [296, 262]

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
        import re

        # PHASE 1: INTELLIGENT DECOMPOSITION
        decomposition_plan = await self.decompose(
            instruction="""Break this problem into minimal, logically independent subproblems. For each:
            - Identify the mathematical domain (combinatorics, algebra, geometry, etc.)
            - Specify required techniques (induction, coordinate transform, modular arithmetic, etc.)
            - List explicit and implicit constraints
            - Define success criteria for the subproblem
            - Note dependencies on other subproblems
            Return as structured list with 'id', 'description', 'dependencies'.""",
            context=""
        )

        # PHASE 2: PARALLEL SUBPROBLEM EXPLORATION
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            
            # Generate multiple solution approaches in parallel
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""APPROACH 1: Analytical
                    Solve subproblem {sp_id}: {sp_desc}
                    Use pure mathematical reasoning, theorems, and identities.
                    Show all steps. Verify each logical leap.
                    If stuck, identify why and suggest alternatives.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""APPROACH 2: Computational
                    Solve subproblem {sp_id}: {sp_desc}
                    Design an algorithm or computation strategy.
                    If applicable, prepare for Programmer execution.
                    Estimate complexity and feasibility.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""APPROACH 3: Transformative
                    Solve subproblem {sp_id}: {sp_desc}
                    Apply non-obvious transformations: change of variables, 
                    symmetry exploitation, duality, or representation shift.
                    Justify why the transformation is valid and useful.""",
                    context=""
                )
            )
            
            # Synthesize best elements
            synthesis = await self.ensemble(
                instruction=f"""Synthesize the three approaches for subproblem {sp_id}.
                - Preserve rigorous proofs from Analytical
                - Incorporate computational insights if valid
                - Integrate transformative insights if they simplify
                - Resolve contradictions
                - Output must be self-contained and verifiable""",
                contexts_list=approaches
            )
            
            # Verify and refine
            verified = await self.revise(
                instruction=f"""CRITICAL VERIFICATION for subproblem {sp_id}:
                - Check all mathematical steps for errors
                - Validate against constraints from decomposition
                - Test edge cases and boundary conditions
                - Ensure answer format matches requirements
                - If any doubt remains, flag for re-computation""",
                context=synthesis
            )
            
            return {"id": sp_id, "solution": verified}

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition_plan]
        )

        # PHASE 3: GLOBAL SYNTHESIS
        solution_fragments = [sp["solution"] for sp in subproblem_solutions]
        integrated_solution = await self.ensemble(
            instruction="""INTEGRATE ALL SUBPROBLEM SOLUTIONS:
            - Reconstruct the complete solution path
            - Ensure logical flow between subproblems
            - Resolve any global constraints or consistency checks
            - Verify the final answer meets domain requirements (integer 000-999)
            - Present as a coherent, competition-ready proof""",
            contexts_list=solution_fragments
        )

        # PHASE 4: COMPUTATIONAL VERIFICATION (if applicable)
        # Check if problem involves computation that can be code-verified
        needs_computation = await self.generate(
            instruction="""Does the final solution involve computational steps 
            (summations, recursions, enumerations, probability calculations) 
            that can be independently verified by code?
            Answer strictly: YES or NO""",
            context=integrated_solution
        )

        if "YES" in needs_computation.upper():
            code_verification = await self.programmer(
                instruction=f"""Generate Python code to verify the computational 
                core of the solution. The code must:
                - Be self-contained
                - Match the mathematical logic exactly
                - Output only the final integer answer (000-999)
                - Include assertions for critical intermediate values
                Context: {integrated_solution}""",
                context=integrated_solution,
                max_retries=3
            )
            
            # Reconcile analytical and computational results
            final_answer = await self.ensemble(
                instruction="""RECONCILE analytical and computational results:
                - If they agree, proceed with confidence
                - If they disagree, identify source of discrepancy
                - Revise analytical solution if code is provably correct
                - Never override analytical proof with code unless code is exhaustive""",
                contexts_list=[integrated_solution, code_verification]
            )
        else:
            final_answer = integrated_solution

        # PHASE 5: FINAL POLISH AND FORMAT ENFORCEMENT
        competition_ready = await self.revise(
            instruction="""FINAL COMPETITION PREPARATION:
            - Extract the numerical answer (must be integer 000-999)
            - Zero-pad to three digits if necessary
            - Present ONLY the final answer in boxed format: \\boxed{ABC}
            - Remove all intermediate steps, explanations, and reasoning
            - If multiple answers possible, select the one matching all constraints
            - If no valid answer found, return \\boxed{000} as fallback""",
            context=final_answer
        )

        # EXTRACTION: Ensure pure numeric output
        # Use regex to extract boxed answer
        match = re.search(r'\\boxed\{(\d{3})\}', competition_ready)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any 3-digit number
            numbers = re.findall(r'\b\d{3}\b', competition_ready)
            if numbers:
                return numbers[0]
            else:
                return "000"  # Ultimate fallback