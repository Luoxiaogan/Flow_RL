# Workflow ID: mgsmbn_35_0
# Benchmark: mgsmbn
# Data Indices: [152]

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

        # Step 1: Assess solvability - gatekeeper for underspecified problems
        solvability_check = await self.generate(
            instruction="""Determine if this problem contains sufficient information to yield a unique numerical answer.
            - Identify if all required quantities are provided
            - Check for logical consistency
            - If answer cannot be determined, respond exactly: 'INSUFFICIENT_DATA'
            - Otherwise, respond: 'SOLVABLE'
            Do not attempt to solve yet. Only assess solvability.""",
            context=""
        )
        
        if "INSUFFICIENT_DATA" in solvability_check:
            return "0"  # Default fallback, though ideally should raise error

        # Step 2: Hierarchical decomposition into subproblems
        subproblems = await self.decompose(
            instruction="""Break this problem into essential subproblems. Structure as:
            [
                {
                    "id": "sp1",
                    "description": "Extract all numerical values and their associated units/entities",
                    "dependencies": ""
                },
                {
                    "id": "sp2",
                    "description": "Identify mathematical relationships and operations needed",
                    "dependencies": "sp1"
                },
                {
                    "id": "sp3",
                    "description": "Check for unit consistency and required conversions",
                    "dependencies": "sp1,sp2"
                },
                {
                    "id": "sp4",
                    "description": "Determine if problem involves conditional logic or branching scenarios",
                    "dependencies": "sp2"
                }
            ]
            Focus on mathematical essence, not linguistic structure.""",
            context=""
        )

        # Step 3: Solve subproblems in dependency order
        solutions = {}
        for sp in subproblems:
            deps = sp['dependencies'].split(',') if sp['dependencies'] else []
            context_pieces = [solutions[dep_id] for dep_id in deps if dep_id in solutions]
            context = "\n".join(context_pieces) if context_pieces else ""
            
            solution = await self.generate(
                instruction=f"""Solve subproblem: {sp['description']}
                Use previous solutions if available: {context}
                Be precise, include units, and flag any inconsistencies.
                If conversion needed, specify both original and converted values.""",
                context=context
            )
            solutions[sp['id']] = solution

        # Step 4: Classify problem type for strategy selection
        problem_classification = await self.generate(
            instruction=f"""Classify this problem based on its mathematical structure:
            - Is it LINEAR (single sequence of operations)?
            - BRANCHING (if-else conditions, multiple scenarios)?
            - ITERATIVE (repeated operations, loops)?
            - PROPORTIONAL (ratios, scaling, percentages)?
            Also identify:
            - Primary unknown to solve for
            - Key formula or relationship
            - Potential pitfalls (unit mismatches, hidden steps)
            Base classification on subproblem solutions: {solutions}""",
            context=""
        )

        # Step 5: Parallel solution generation from multiple perspectives
        perspectives = [
            "Solve using dimensional analysis: track units at every step",
            "Solve using algebraic modeling: define variables and equations",
            "Solve using step-by-step arithmetic: show each calculation explicitly"
        ]
        
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{perspective}
                Problem classification: {problem_classification}
                Subproblem solutions: {solutions}
                Show all work. Final answer must be a single numerical value.
                If units need conversion, do it explicitly.
                If branching, explore all paths and state which is valid.""",
                context=""
            ) for perspective in perspectives]
        )

        # Step 6: Ensemble - select best solution with reasoning
        best_solution = await self.ensemble(
            instruction="""Select the most reliable solution by evaluating:
            - Unit consistency throughout
            - Mathematical correctness
            - Alignment with problem constraints
            - Clarity of steps
            - Handling of edge cases (negative values, fractions where inappropriate)
            Reject solutions that:
            - Skip unit conversions
            - Assume unstated values
            - Produce non-numeric or multiple answers
            Explain why the chosen solution is best and why others were rejected.
            Extract ONLY the final numerical answer from the chosen solution.""",
            contexts_list=solution_attempts
        )

        # Step 7: Validate with executable code
        code_validation = await self.programmer(
            instruction=f"""Convert the following reasoning into Python code:
            {best_solution}
            Requirements:
            - Include assertions for unit conversions
            - Check for non-negative results where appropriate
            - Validate against problem constraints
            - Output must be a single number (int or float)
            If code fails, revise reasoning and retry (max 3 attempts).""",
            context=best_solution,
            max_retries=3
        )

        # Step 8: Final context-aware revision
        final_answer = await self.revise(
            instruction=f"""Given the computed result: {code_validation}
            Verify it makes real-world sense:
            - Can the answer be fractional? (e.g., people, whole items)
            - Does it match the problem's scale? (e.g., not millions when expecting dozens)
            - Are units correct? (e.g., hours vs minutes)
            If revision needed, adjust and explain why.
            Final output must be ONLY the numerical value, nothing else.""",
            context=code_validation
        )

        # Extract just the number (handle cases where explanation is included)
        # Use regex to find the first standalone number
        match = re.search(r'(-?\d+\.?\d*)', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()