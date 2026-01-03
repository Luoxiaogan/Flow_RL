# Workflow ID: limr_100_0
# Benchmark: limr
# Data Indices: [29, 280]

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
        import json
        import re
        
        # Stage 1: Problem Classification (Parallel Perspectives)
        classification_attempts = await asyncio.gather(
            self.generate(
                instruction="""Analyze the problem and classify it with extreme precision. Consider:
                - Primary domain (algebra, combinatorics, number theory, geometry, etc.)
                - Specific sub-type (functional equation, Diophantine, counting, optimization, etc.)
                - Key constraints and boundary conditions
                - Expected solution form (integer, set of values, proof, etc.)
                - Likely techniques (substitution, induction, generating functions, modular arithmetic, etc.)
                - Potential pitfalls or non-obvious insights
                Format as a structured JSON with keys: domain, subtype, constraints, techniques, solution_form.""",
                context=""
            ),
            self.generate(
                instruction="""Approach classification from first principles. Ignore standard categories. Ask:
                - What is the core object being manipulated? (functions, numbers, sets, shapes, etc.)
                - What is the goal? (find value, prove property, count configurations, etc.)
                - What makes this problem non-trivial? (hidden symmetry, edge cases, counterintuitive result, etc.)
                - What minimal set of mathematical tools could solve it?
                Format as JSON with keys: core_object, goal, complexity_source, minimal_tools.""",
                context=""
            )
        )
        
        # Refine classifications
        refined_classifications = await asyncio.gather(
            *[self.revise(
                instruction="""Improve this classification:
                - Ensure all constraints from original problem are accounted for
                - Specify exact mathematical techniques (not just "algebra")
                - Identify any implicit assumptions
                - Cross-validate with problem's answer format requirement (integer 000-999)
                - Flag any ambiguities or edge cases that need special handling""",
                context=attempt
            ) for attempt in classification_attempts]
        )
        
        # Ensemble to unified classification
        final_classification = await self.ensemble(
            instruction="""Synthesize these classification attempts into one authoritative analysis. Resolve conflicts by:
            - Prioritizing specificity over generality
            - Favoring classifications that account for all constraints
            - Selecting techniques that match the problem's likely solution path
            - Ensuring compatibility with integer answer requirement
            Output as comprehensive JSON with keys: domain, subtype, constraints, required_techniques, solution_strategy, edge_cases.""",
            contexts_list=refined_classifications
        )
        
        # Stage 2: Strategic Decomposition
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem using the classification: {final_classification}
            
            Create subproblems that:
            - Are mathematically independent where possible
            - Have clear dependencies when sequential reasoning is required
            - Each can be solved with a single technique or insight
            - Include verification steps as separate subproblems
            - Cover all edge cases identified in classification
            
            For each subproblem, specify:
            - What needs to be found/proved
            - What inputs it requires from other subproblems
            - What technique to apply (be specific: "use substitution x=1/y", not just "substitution")
            - How to validate the result
            
            Prioritize subproblems that can unlock multiple solution paths.""",
            context=""
        )
        
        # Track solved subproblems
        solved_subproblems = {}
        subproblem_attempts = {}
        
        # Stage 3: Iterative Subproblem Resolution
        max_iterations = 5
        for iteration in range(max_iterations):
            # Find subproblems whose dependencies are satisfied
            ready_subproblems = []
            for sub in decomposition:
                sub_id = sub['id']
                if sub_id in solved_subproblems:
                    continue
                deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
                if all(dep.strip() in solved_subproblems for dep in deps if dep.strip()):
                    ready_subproblems.append(sub)
            
            if not ready_subproblems:
                break  # No more subproblems can be solved
            
            # Solve ready subproblems in parallel
            solve_tasks = []
            for sub in ready_subproblems:
                sub_id = sub['id']
                # Construct context from dependencies
                dep_context = "\n".join([f"From {dep_id}: {solved_subproblems[dep_id]}" 
                                       for dep_id in sub.get('dependencies', '').split(',') 
                                       if dep_id.strip() and dep_id.strip() in solved_subproblems])
                
                # Choose solver based on subproblem type
                if any(kw in sub['description'].lower() for kw in ['compute', 'calculate', 'number of', 'sum', 'product']):
                    task = self.programmer(
                        instruction=f"""Solve this subproblem: {sub['description']}
                        
                        Context from dependencies:
                        {dep_context}
                        
                        Classification context: {final_classification}
                        
                        Requirements:
                        - Show all steps if symbolic, or provide code if computational
                        - Verify result satisfies all constraints
                        - Output final answer clearly
                        - If multiple solutions, list all""",
                        context=dep_context
                    )
                else:
                    task = self.generate(
                        instruction=f"""Solve this mathematical subproblem: {sub['description']}
                        
                        Use technique: {sub.get('technique', 'appropriate mathematical reasoning')}
                        
                        Context from dependencies:
                        {dep_context}
                        
                        Classification: {final_classification}
                        
                        Requirements:
                        - Provide rigorous mathematical reasoning
                        - Include verification step
                        - State any assumptions made
                        - Box final result""",
                        context=dep_context
                    )
                solve_tasks.append((sub_id, task))
            
            # Execute in parallel
            if solve_tasks:
                results = await asyncio.gather(*[task for _, task in solve_tasks], return_exceptions=True)
                for (sub_id, _), result in zip(solve_tasks, results):
                    if isinstance(result, Exception):
                        subproblem_attempts[sub_id] = f"ERROR: {str(result)}"
                    else:
                        # Validate solution
                        validated = await self.revise(
                            instruction=f"""Validate this subproblem solution:
                            - Does it satisfy all original problem constraints?
                            - Is the reasoning mathematically sound?
                            - Are edge cases handled?
                            - Does it match the expected format?
                            - If computational, is precision maintained?
                            Flag any issues. If valid, return solution unchanged.""",
                            context=str(result)
                        )
                        solved_subproblems[sub_id] = validated
                        subproblem_attempts[sub_id] = validated
        
        # Stage 4: Synthesis and Final Answer Extraction
        all_solutions_context = "\n\n".join([f"Subproblem {sub_id}: {solution}" 
                                           for sub_id, solution in solved_subproblems.items()])
        
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize all subproblem solutions into a complete answer:
            
            Subproblem solutions:
            {all_solutions_context}
            
            Original classification: {final_classification}
            
            Requirements:
            - Combine partial results into final answer
            - Ensure global consistency (no contradictions between subproblems)
            - Handle any remaining edge cases
            - Extract the final integer answer between 000-999 as required
            - If multiple values possible, compute n × s as specified
            - Present final answer in boxed format: \\boxed{{answer}}""",
            contexts_list=[all_solutions_context]
        )
        
        # Stage 5: Final Verification and Answer Extraction
        final_answer = await self.programmer(
            instruction=f"""Extract the final numerical answer from this solution:
            
            {synthesized_solution}
            
            Requirements:
            - The answer must be an integer between 000 and 999
            - If solution contains multiple steps, compute the final result
            - If answer is in form n × s, compute the product
            - Return ONLY the integer, no text or formatting
            - If uncertain, return 000""",
            context=synthesized_solution
        )
        
        # Clean and return final answer
        # Extract number from any text
        match = re.search(r'\b(\d{1,3})\b', str(final_answer))
        if match:
            answer = int(match.group(1))
            # Ensure 000-999 range
            return min(max(answer, 0), 999)
        else:
            # Fallback: try to compute from synthesis
            fallback = await self.programmer(
                instruction="The solution is complete but answer extraction failed. Compute n × s from the context. Return only integer 000-999.",
                context=synthesized_solution
            )
            match = re.search(r'\b(\d{1,3})\b', str(fallback))
            if match:
                answer = int(match.group(1))
                return min(max(answer, 0), 999)
            else:
                return 0  # Ultimate fallback