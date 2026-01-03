# Workflow ID: mbppplus_83_0
# Benchmark: mbppplus
# Data Indices: [129, 102]

import asyncio

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
        import json

        # PHASE 1: ANALYZE — Understand problem type, constraints, edge cases
        analysis = await self.generate(
            instruction="""Perform deep problem analysis. Answer these questions:
            1. What is the primary data type being manipulated? (list, tuple, dict, string, number)
            2. What is the expected return type? Must it match input type?
            3. Does order matter in the output?
            4. Should duplicates be preserved, removed, or handled specially?
            5. What are the edge cases? (empty input, single element, all same elements, None, mixed types)
            6. Is this a lookup, transformation, filtering, or algorithmic problem?
            7. Are there any implied performance constraints?
            8. Can this be solved with a built-in Python function or itertools?
            Format your answer as a structured JSON-like summary.""",
            context=""
        )

        # PHASE 2: STRATEGIZE — Decide approach based on analysis
        # Branch 1: Simple problems (direct lookup, basic membership)
        if any(keyword in analysis.lower() for keyword in ["lookup", "membership", "key", "exists", "present"]):
            strategy = "direct"
        # Branch 2: Algorithmic or requires decomposition
        elif any(keyword in analysis.lower() for keyword in ["consecutive", "sequence", "group", "pattern", "sort", "filter"]):
            strategy = "algorithmic"
        else:
            strategy = "generic"

        # Generate multiple solution hypotheses in parallel
        solution_attempts = []
        
        # Hypothesis 1: Elegant one-liner using built-ins
        solution1 = await self.generate(
            instruction=f"""Generate a Python function that solves the problem using the most elegant, Pythonic approach.
            Consider using itertools, comprehensions, or built-in functions.
            Analysis context: {analysis}
            Ensure edge cases are handled. Preserve types and order as required.
            Return ONLY the function implementation with necessary imports.""",
            context=analysis
        )
        solution_attempts.append(solution1)

        # Hypothesis 2: Explicit, readable step-by-step approach
        solution2 = await self.generate(
            instruction=f"""Generate a Python function that solves the problem using explicit, readable steps.
            Avoid clever one-liners. Prioritize clarity and robustness.
            Analysis context: {analysis}
            Include guard clauses for edge cases. Use descriptive variable names.
            Return ONLY the function implementation with necessary imports.""",
            context=analysis
        )
        solution_attempts.append(solution2)

        # If algorithmic, also try decomposition
        if strategy == "algorithmic":
            decomposition = await self.decompose(
                instruction=f"""Break this problem into minimal, ordered subproblems.
                Each subproblem should be independently solvable.
                Analysis context: {analysis}""",
                context=analysis
            )
            
            # Solve subproblems in dependency order
            sub_solutions = {}
            for sub in decomposition:
                deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
                # Wait for dependencies (simplified: assume linear order)
                dep_context = "\n".join([sub_solutions.get(d.strip(), "") for d in deps if d.strip() in sub_solutions])
                
                sub_sol = await self.generate(
                    instruction=f"""Solve this subproblem: {sub['description']}
                    Previous steps: {dep_context}
                    Analysis context: {analysis}
                    Return ONLY the code snippet or logic needed for this step.""",
                    context=dep_context
                )
                sub_solutions[sub['id']] = sub_sol
            
            # Synthesize final solution from subproblems
            synthesized = await self.generate(
                instruction=f"""Combine these subproblem solutions into a complete function:
                {json.dumps(sub_solutions, indent=2)}
                Analysis context: {analysis}
                Ensure the final function matches the required signature and handles edge cases.
                Return ONLY the complete function implementation with imports.""",
                context=json.dumps(sub_solutions)
            )
            solution_attempts.append(synthesized)

        # PHASE 3: ENSEMBLE & VALIDATE — Select best solution
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness (handles all edge cases from analysis)
            2. Readability and maintainability
            3. Efficiency (avoid unnecessary loops or data structures)
            4. Type safety (preserves input/output types)
            5. Pythonic style
            Return ONLY the selected function implementation.""",
            contexts_list=solution_attempts
        )

        # PHASE 4: REVISE & REFINE — Critique and improve
        for iteration in range(3):  # Up to 3 refinement rounds
            critique = await self.revise(
                instruction=f"""Critically review this solution:
                1. Does it handle ALL edge cases mentioned in analysis: {analysis}?
                2. Does it preserve type and order as required?
                3. Is there any potential bug or inefficiency?
                4. Can it be made more robust or readable?
                If no issues, return 'APPROVED'. Otherwise, describe fixes needed.""",
                context=selected_solution
            )
            
            if "APPROVED" in critique.upper():
                break
                
            # Apply fixes
            selected_solution = await self.revise(
                instruction=f"""Revise the solution to address these issues: {critique}
                Maintain all correct behavior while fixing the problems.
                Return ONLY the revised function implementation.""",
                context=selected_solution
            )

        # FINAL OUTPUT
        return selected_solution