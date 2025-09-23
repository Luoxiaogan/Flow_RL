# Workflow ID: limr_110_0
# Benchmark: limr
# Data Indices: [190, 48]

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

        # Stage 1: Deep Decomposition
        decomposition = await self.decompose(
            instruction="""Break this problem into the smallest logically independent subproblems possible. 
            For each subproblem:
            - Clearly state what needs to be solved
            - Identify if it's primarily computational, conceptual, or hybrid
            - Note any dependencies on other subproblems
            - Flag if it requires integer output, proof, or optimization
            Return structured subproblems with IDs and dependency chains.""",
            context=""
        )

        # Stage 2: Parallel Subproblem Processing
        subproblem_tasks = []
        subproblem_contexts = {}
        
        for sub in decomposition:
            sub_id = sub['id']
            desc = sub['description']
            
            # Dynamic instruction based on subproblem type
            solve_instruction = f"""Solve this subproblem: {desc}
            Strategy:
            - If computational: derive exact formulas, then use code for evaluation
            - If conceptual: construct logical proof with clear steps
            - If hybrid: do both and reconcile
            - Maintain precision: final answer must be integer 000-999 if applicable
            - Show all work and assumptions
            - Verify internal consistency"""
            
            task = self.generate(
                instruction=solve_instruction,
                context=""
            )
            subproblem_tasks.append(task)
            subproblem_contexts[sub_id] = {"description": desc, "task": task}

        # Execute all subproblem solutions in parallel
        solutions = await asyncio.gather(*[sub["task"] for sub in subproblem_contexts.values()])
        
        # Map solutions back to subproblem IDs
        for i, sub_id in enumerate(subproblem_contexts.keys()):
            subproblem_contexts[sub_id]["solution"] = solutions[i]

        # Stage 3: Adversarial Validation
        validation_tasks = []
        for sub_id, data in subproblem_contexts.items():
            validation_instruction = f"""Critically evaluate this solution for subproblem {sub_id}: {data['description']}
            - Check for logical flaws or gaps
            - Verify computational accuracy if applicable
            - Ensure integer constraint (000-999) is respected
            - Identify any unstated assumptions
            - Suggest improvements or alternatives
            Return 'VALID' if flawless, otherwise detailed critique."""
            
            validation_tasks.append(
                self.generate(instruction=validation_instruction, context=data["solution"])
            )
        
        validations = await asyncio.gather(*validation_tasks)
        
        # Stage 4: Conditional Revision or Recomposition
        revised_solutions = {}
        for i, (sub_id, data) in enumerate(subproblem_contexts.items()):
            validation = validations[i]
            if "VALID" in validation.upper() and "FLAW" not in validation.upper() and "ERROR" not in validation.upper():
                revised_solutions[sub_id] = data["solution"]
            else:
                # Trigger revision with critique
                revised = await self.revise(
                    instruction=f"""Improve this solution based on critique: {validation}
                    - Fix all identified errors
                    - Strengthen weak arguments
                    - Add missing steps
                    - Ensure integer output constraint
                    - Maintain mathematical rigor""",
                    context=data["solution"]
                )
                revised_solutions[sub_id] = revised

        # Stage 5: Dependency-Aware Synthesis
        # Build solution in dependency order
        solved_subproblems = {}
        remaining = set(revised_solutions.keys())
        
        while remaining:
            progress = False
            for sub in decomposition:
                sub_id = sub['id']
                if sub_id in solved_subproblems:
                    continue
                    
                deps = sub.get('dependencies', "").split(",") if sub.get('dependencies') else []
                deps = [d.strip() for d in deps if d.strip()]
                
                if all(d in solved_subproblems for d in deps):
                    # All dependencies satisfied, synthesize this subproblem
                    context_chain = "\n\n".join([f"Subproblem {d}: {solved_subproblems[d]}" for d in deps]) if deps else ""
                    synthesis_instruction = f"""Integrate this subproblem solution with its dependencies:
                    Subproblem: {sub['description']}
                    Solution: {revised_solutions[sub_id]}
                    Dependencies: {context_chain}
                    
                    Produce a unified, coherent solution segment that flows logically from dependencies."""
                    
                    synthesized = await self.generate(
                        instruction=synthesis_instruction,
                        context=revised_solutions[sub_id]
                    )
                    solved_subproblems[sub_id] = synthesized
                    remaining.remove(sub_id)
                    progress = True
            
            if not progress:
                # Circular dependency or missing - break with best effort
                break

        # Stage 6: Global Ensemble and Final Answer Extraction
        all_solutions = list(solved_subproblems.values())
        if len(all_solutions) == 0:
            all_solutions = list(revised_solutions.values())
            
        final_synthesis = await self.ensemble(
            instruction="""Synthesize all solution fragments into a single coherent answer.
            - Resolve any contradictions
            - Fill gaps using strongest available reasoning
            - Ensure final output is a single integer between 000 and 999
            - If multiple answers emerge, select the one with strongest validation
            - Format as exactly three digits (e.g., '042', not '42')""",
            contexts_list=all_solutions
        )

        # Stage 7: Final Formatting and Verification
        formatted_answer = await self.revise(
            instruction="""Extract the final integer answer from this solution.
            - Must be exactly 3 digits (000-999)
            - Remove all explanatory text
            - If answer is not integer, derive closest valid integer
            - If multiple candidates, pick most mathematically justified
            - Return ONLY the three-digit number, nothing else""",
            context=final_synthesis
        )

        # Clean and ensure format
        digits = re.sub(r'\D', '', formatted_answer)
        if len(digits) == 1:
            digits = "00" + digits
        elif len(digits) == 2:
            digits = "0" + digits
        elif len(digits) > 3:
            digits = digits[-3:]  # Take last 3 digits as fallback
            
        return digits[:3]  # Ensure exactly 3 digits