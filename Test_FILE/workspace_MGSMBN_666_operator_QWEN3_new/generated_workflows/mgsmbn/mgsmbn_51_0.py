# Workflow ID: mgsmbn_51_0
# Benchmark: mgsmbn
# Data Indices: [196, 77]

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

        # STAGE 1: Problem Classification and Initial Decomposition
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali word problem and classify its type and structure:
            1. Identify the core mathematical concept (sequential operations, proportions, distribution, comparison, multi-entity tracking, etc.)
            2. List all named entities (people, objects) and their initial quantities
            3. Identify all actions (giving, taking, moving, converting) and their sequence
            4. Note any hidden constraints (non-negative, integer-only, real-world plausibility)
            5. Determine if solution requires forward calculation, backward reasoning, or algebraic setup
            6. Suggest the optimal solution strategy
            Format your response as a structured JSON-like outline with clear sections.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems based on the classification:
            - Each subproblem should isolate one unknown or one calculation step
            - Specify dependencies: which subproblems must be solved before others
            - Include the mathematical relationship or operation needed for each
            - Flag any subproblem that requires unit conversion or constraint checking
            Prioritize decomposition that enables parallel solving where possible.""",
            context=classification
        )

        # STAGE 2: Parallel Subproblem Solving with Validation
        async def solve_subproblem(subproblem_desc: str, subproblem_id: str) -> str:
            # Generate step-by-step reasoning for this subproblem
            reasoning = await self.generate(
                instruction=f"""Solve subproblem {subproblem_id}: {subproblem_desc}
                - Show all intermediate steps explicitly
                - Define variables if needed
                - Justify each operation with reference to the original problem
                - Include unit tracking throughout
                - Double-check for real-world plausibility (no negative fries, fractional cars unless allowed)""",
                context=classification
            )
            
            # Attempt programmatic solution
            code_solution = await self.programmer(
                instruction=f"""Convert this reasoning into executable Python code:
                - Define all variables clearly
                - Include assertions for constraints (e.g., assert result >= 0)
                - Return only the numerical answer
                - If multiple steps, show intermediate variables
                - Handle edge cases explicitly""",
                context=reasoning,
                max_retries=3
            )
            
            # Validate and revise if needed
            validation = await self.revise(
                instruction="""Critically validate this solution:
                1. Does the code logic match the reasoning?
                2. Are all constraints from the original problem respected?
                3. Is the answer plausible in real-world context?
                4. Are units consistent throughout?
                If any issue is found, revise the solution to fix it. Otherwise, return the solution unchanged.""",
                context=f"Reasoning: {reasoning}

Code Solution: {code_solution}"
            )
            
            return validation

        # Solve independent subproblems in parallel
        subproblem_tasks = []
        dependency_map = {}
        
        for sub in decomposition:
            sub_id = sub['id']
            deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
            dependency_map[sub_id] = [d.strip() for d in deps if d.strip()]
            subproblem_tasks.append((sub_id, sub['description']))
        
        # Simple topological sort for sequencing (for this domain, dependencies are shallow)
        solved_subproblems = {}
        remaining = subproblem_tasks.copy()
        
        # Iteratively solve subproblems whose dependencies are met
        final_answer = None
        iteration = 0
        max_iterations = len(decomposition) + 2  # Safety limit
        
        while remaining and iteration < max_iterations:
            iteration += 1
            solvable_now = []
            new_remaining = []
            
            for sub_id, desc in remaining:
                deps = dependency_map.get(sub_id, [])
                if all(dep in solved_subproblems for dep in deps):
                    solvable_now.append((sub_id, desc))
                else:
                    new_remaining.append((sub_id, desc))
            
            if not solvable_now:
                # Deadlock - force solve one to break cycle (rare in this domain)
                solvable_now = [remaining[0]]
                new_remaining = remaining[1:]
            
            # Solve solvable subproblems in parallel
            solutions = await asyncio.gather(
                *[solve_subproblem(desc, sub_id) for sub_id, desc in solvable_now]
            )
            
            for (sub_id, _), solution in zip(solvable_now, solutions):
                solved_subproblems[sub_id] = solution
            
            remaining = new_remaining
        
        # STAGE 3: Synthesize Final Answer
        synthesis_context = "\n\n".join([
            f"Subproblem {sub_id}: {solution}" 
            for sub_id, solution in solved_subproblems.items()
        ])
        
        synthesized = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into the final answer:
            - Cross-validate that all subproblem results are consistent with each other
            - Ensure the final answer directly addresses the original question
            - If there are conflicting results, identify the most reliable one based on constraint adherence
            - Extract ONLY the numerical answer as specified in the problem
            - Format as a single number (integer or decimal) with no units or explanation""",
            contexts_list=list(solved_subproblems.values())
        )
        
        # STAGE 4: Final Validation and Extraction
        final_answer = await self.revise(
            instruction="""Extract and validate the final numerical answer:
            1. From the synthesized result, extract ONLY the number (integer or decimal)
            2. Verify it matches the problem's requested quantity (e.g., "how many fries" not "how many people")
            3. Re-check against original problem constraints (non-negative, integer if required)
            4. If any mismatch, re-calculate using the most reliable subproblem chain
            5. Return ONLY the number, nothing else""",
            context=f"Synthesized: {synthesized}

Original Classification: {classification}"
        )
        
        # Clean extraction (in case revision added text)
        # Simple number extraction - works for integers and decimals
        import re
        numbers = re.findall(r'-?\d+\.?\d*', final_answer)
        if numbers:
            return numbers[0]
        else:
            # Fallback: return as-is and let evaluation handle it
            return final_answer.strip()