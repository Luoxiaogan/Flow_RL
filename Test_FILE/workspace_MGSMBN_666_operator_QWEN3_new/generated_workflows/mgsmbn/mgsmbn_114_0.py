# Workflow ID: mgsmbn_114_0
# Benchmark: mgsmbn
# Data Indices: [192, 137]

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

        # PHASE 1: SEMANTIC DECOMPOSITION & CLASSIFICATION (PARALLEL)
        decomposition_task = self.decompose(
            instruction="""Break this Bengali math problem into atomic, mathematically meaningful subproblems.
            Each subproblem must:
            - Represent a single calculable step
            - Specify input dependencies (which previous subproblems it relies on)
            - Identify the mathematical operation required (addition, subtraction, multiplication, division, percentage, fraction, etc.)
            - Preserve unit context (টাকা, মাইল, জন, etc.)
            - Handle implicit operations (e.g., "অবশিষ্ট" implies subtraction from previous total)
            Return as structured list with 'id', 'description', 'dependencies'.""",
            context=""
        )

        classification_task = self.generate(
            instruction="""Classify this problem's core mathematical structure:
            1. Primary category: Sequential Operations / Rate Problems / Proportional Reasoning / Distribution / Comparison / Multi-entity
            2. Required operations: List all arithmetic operations needed in order
            3. Hidden steps: Identify any intermediate calculations not explicitly stated
            4. Unit handling: Specify how units transform through operations
            5. Constraints: Note any real-world constraints (non-negative, integer-only, etc.)
            Format as JSON with keys: category, operations, hidden_steps, units, constraints.""",
            context=""
        )

        decomposition, classification = await asyncio.gather(decomposition_task, classification_task)

        # PHASE 2: VALIDATE & ENRICH DECOMPOSITION
        validated_decomposition = await self.revise(
            instruction=f"""Validate and enhance the decomposition using classification:
            Classification: {classification}
            
            For each subproblem:
            - Verify mathematical operation aligns with problem category
            - Ensure dependencies correctly reflect calculation order
            - Add unit tracking annotations
            - Insert hidden steps if missing
            - Flag any potential constraint violations
            Return revised decomposition in same structured format.""",
            context=json.dumps(decomposition)
        )

        # PHASE 3: CONDITIONAL SOLUTION PATHWAY
        classification_data = json.loads(classification)
        category = classification_data.get("category", "").lower()

        if "proportional" in category or "percentage" in category or "fraction" in category:
            # Use algebraic modeling for proportional problems
            solution_approach = "algebraic"
        elif "sequential" in category or "multi-entity" in category:
            # Use iterative state tracking
            solution_approach = "iterative"
        else:
            # Default to direct computation
            solution_approach = "direct"

        # PHASE 4: DEPENDENCY-ORDERED EXECUTION WITH VALIDATION
        subproblems = json.loads(validated_decomposition)
        solutions = {}
        
        # Topological sort by dependencies
        solved_ids = set()
        remaining = subproblems.copy()

        while remaining:
            executable = [
                sp for sp in remaining 
                if all(dep.strip() in solved_ids for dep in sp.get('dependencies', '').split(',') if dep.strip())
            ]
            
            if not executable:
                break  # Circular dependency or missing base case

            # Solve executable subproblems in parallel
            solve_tasks = []
            for sp in executable:
                solve_task = self.programmer(
                    instruction=f"""Solve this subproblem using {solution_approach} approach:
                    Subproblem: {sp['description']}
                    Dependencies: {[solutions.get(dep.strip(), 'N/A') for dep in sp.get('dependencies', '').split(',') if dep.strip()]}
                    Classification context: {classification}
                    Requirements:
                    - Show all steps explicitly
                    - Track units throughout
                    - Validate against constraints: {classification_data.get('constraints', [])}
                    - Return only the final numerical result""",
                    context=json.dumps(solutions)
                )
                solve_tasks.append((sp['id'], solve_task))
            
            # Execute in parallel
            results = await asyncio.gather(*[task for _, task in solve_tasks])
            
            # Store results and mark as solved
            for (sp_id, _), result in zip(solve_tasks, results):
                solutions[sp_id] = result
                solved_ids.add(sp_id)
                remaining = [sp for sp in remaining if sp['id'] != sp_id]

        # PHASE 5: ENSEMBLE FINAL ANSWER WITH SANITY CHECK
        final_candidates = []
        
        # Candidate 1: Direct extraction from last subproblem
        if solutions:
            last_solution = list(solutions.values())[-1]
            final_candidates.append(last_solution)

        # Candidate 2: Holistic re-computation
        holistic_solution = await self.programmer(
            instruction=f"""Compute final answer holistically using all subproblem solutions:
            Subproblem Solutions: {json.dumps(solutions)}
            Classification: {classification}
            Requirements:
            - Re-derive final answer from first principles
            - Cross-validate with subproblem results
            - Apply sanity checks: {classification_data.get('constraints', [])}
            - Return only numerical value""",
            context=""
        )
        final_candidates.append(holistic_solution)

        # Candidate 3: Constraint-validated revision
        constrained_solution = await self.revise(
            instruction=f"""Apply real-world constraints to refine solution:
            Current solutions: {final_candidates}
            Constraints: {classification_data.get('constraints', [])}
            Requirements:
            - Ensure non-negative values where appropriate
            - Round to integers if counting discrete entities
            - Reject physically impossible results
            - Return best constrained numerical answer""",
            context=holistic_solution
        )
        final_candidates.append(constrained_solution)

        # PHASE 6: FINAL ENSEMBLE & OUTPUT
        final_answer = await self.ensemble(
            instruction="""Select the most reliable final answer:
            - Prefer solutions that satisfy all constraints
            - Favor consistency across derivation methods
            - Choose numerically stable results
            - Reject any solution with logical inconsistencies
            Return ONLY the final numerical value, nothing else.""",
            contexts_list=final_candidates
        )

        return final_answer