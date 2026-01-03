# Workflow ID: mgsmbn_13_0
# Benchmark: mgsmbn
# Data Indices: [181]

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
        from collections import defaultdict

        # STEP 1: Deep Structural Decomposition
        decomposition_instruction = """
        Break down this Bengali word problem into atomic, solvable subproblems. For each subproblem:
        - Assign a unique ID (e.g., "SP1", "SP2")
        - Describe what needs to be calculated or determined
        - Specify dependencies (other subproblem IDs that must be solved first)
        - Classify type: "compute" (requires calculation), "interpret" (requires semantic understanding), "validate" (requires checking constraints), or "relate" (requires combining results)
        - Extract and tag all entities, units, and numerical values involved
        - Note any implicit constraints (e.g., non-negative values, integer-only answers)
        
        Example format:
        [
          {
            "id": "SP1",
            "description": "Calculate Carlos's total cost: 3 hours × 30 টাকা/ঘণ্টা",
            "dependencies": "",
            "type": "compute",
            "entities": ["Carlos", "30 টাকা/ঘণ্টা", "3 ঘণ্টা"],
            "units": ["টাকা"],
            "constraints": ["non-negative"]
          }
        ]
        
        Ensure the decomposition reflects the causal and temporal structure of the problem.
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Build dependency graph
        dependency_graph = {sp['id']: sp.get('dependencies', '').split(',') if sp.get('dependencies') else [] for sp in subproblems}
        solved = {}
        results_log = []

        # Topological sort helper
        def get_execution_order(graph):
            indegree = defaultdict(int)
            for node, deps in graph.items():
                for dep in deps:
                    if dep.strip():
                        indegree[node] += 1
            queue = [node for node in graph if indegree[node] == 0]
            order = []
            while queue:
                node = queue.pop(0)
                order.append(node)
                for n, deps in graph.items():
                    if node in [d.strip() for d in deps]:
                        indegree[n] -= 1
                        if indegree[n] == 0:
                            queue.append(n)
            return order

        execution_order = get_execution_order(dependency_graph)

        # STEP 2: Solve Subproblems in Dependency Order
        for sp_id in execution_order:
            sp = next(s for s in subproblems if s['id'] == sp_id)
            
            # Build context from dependencies
            dep_context = "\n".join([f"{dep_id}: {solved[dep_id]}" for dep_id in dependency_graph[sp_id] if dep_id.strip() and dep_id in solved])
            
            # Route based on type
            if sp['type'] == 'compute':
                compute_instruction = f"""
                Generate Python code to solve: {sp['description']}
                
                Context from dependencies:
                {dep_context}
                
                Entities and units involved: {sp.get('entities', [])}
                Constraints: {sp.get('constraints', [])}
                
                Requirements:
                - Use exact arithmetic
                - Track units explicitly in comments
                - Validate against constraints (e.g., non-negative)
                - Return only the final numerical result
                """
                
                result = await self.programmer(
                    instruction=compute_instruction,
                    context=dep_context
                )
                
                # Extract numerical result
                match = re.search(r'[-+]?\d*\.\d+|\d+', result)
                if match:
                    solved[sp_id] = match.group()
                else:
                    solved[sp_id] = "ERROR: No numerical result found"
                    
            elif sp['type'] == 'interpret':
                interpret_instruction = f"""
                Resolve semantic ambiguity in: {sp['description']}
                
                Context: {dep_context}
                Problem text: {self.problem_text}
                
                Output format: "Interpretation: [clear restatement of meaning]"
                """
                result = await self.generate(
                    instruction=interpret_instruction,
                    context=dep_context
                )
                solved[sp_id] = result
                
            elif sp['type'] == 'validate':
                validate_instruction = f"""
                Check if {sp['description']} holds given:
                {dep_context}
                
                Return "VALID" or "INVALID: [reason]"
                """
                result = await self.generate(
                    instruction=validate_instruction,
                    context=dep_context
                )
                solved[sp_id] = result
                
            elif sp['type'] == 'relate':
                relate_instruction = f"""
                Combine these results to answer: {sp['description']}
                
                Results: {dep_context}
                
                Return only the final numerical answer.
                """
                result = await self.ensemble(
                    instruction=relate_instruction,
                    contexts_list=[dep_context]
                )
                solved[sp_id] = result
            
            # Validation step for all types
            validation_instruction = f"""
            Validate this result for subproblem {sp_id}: {solved[sp_id]}
            
            Against original problem: {self.problem_text}
            Constraints: {sp.get('constraints', [])}
            Expected unit: {sp.get('units', ['unknown'])[0] if sp.get('units') else 'unknown'}
            
            If invalid, explain why. If valid, return "OK".
            """
            
            validation = await self.revise(
                instruction=validation_instruction,
                context=str(solved[sp_id])
            )
            
            if "OK" not in validation and "VALID" not in validation:
                # Retry with feedback
                retry_instruction = f"""
                Previous attempt failed validation: {validation}
                
                Revised approach for: {sp['description']}
                Context: {dep_context}
                Constraints: {sp.get('constraints', [])}
                """
                
                if sp['type'] == 'compute':
                    result = await self.programmer(
                        instruction=retry_instruction,
                        context=dep_context
                    )
                    match = re.search(r'[-+]?\d*\.\d+|\d+', result)
                    solved[sp_id] = match.group() if match else "ERROR: Retry failed"
                else:
                    result = await self.generate(
                        instruction=retry_instruction,
                        context=dep_context
                    )
                    solved[sp_id] = result
            
            results_log.append(f"{sp_id}: {solved[sp_id]}")

        # STEP 3: Final Answer Synthesis
        final_synthesis_instruction = f"""
        Given all subproblem results:
        {'; '.join(results_log)}
        
        And original question: {self.problem_text}
        
        Synthesize the final answer by:
        1. Identifying which subproblem(s) directly answer the main question
        2. Cross-checking unit consistency
        3. Verifying no constraints are violated
        4. Returning ONLY the final numerical value (no units, no text)
        
        If multiple candidates exist, use ensemble to select the most consistent.
        """
        
        if len(results_log) == 1:
            final_answer = solved[execution_order[0]]
        else:
            final_answer = await self.ensemble(
                instruction=final_synthesis_instruction,
                contexts_list=results_log
            )
        
        # Extract final numerical answer
        final_match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if final_match:
            return final_match.group()
        else:
            # Fallback: return first numerical result
            for result in results_log:
                match = re.search(r'[-+]?\d*\.\d+|\d+', result)
                if match:
                    return match.group()
            return "0"  # Ultimate fallback