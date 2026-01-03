# Workflow ID: mgsmbn_117_0
# Benchmark: mgsmbn
# Data Indices: [112]

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

        # Step 1: Deep structural decomposition
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic, solvable subproblems.
        For each subproblem, identify:
        - The mathematical operation required (addition, percentage, multiplication, etc.)
        - The entities involved (items, people, currencies)
        - Any constraints (must be integer, non-negative, etc.)
        - Dependencies on other subproblems (e.g., "requires result from subproblem 2")
        
        Format each subproblem clearly. Prioritize foundational calculations first.
        Example: "Calculate total cost of sandwiches before tax" → depends on: none
        Example: "Apply 20% delivery fee" → depends on: subproblem 1 (subtotal)
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Build dependency graph
        dependency_graph = {sp['id']: sp for sp in subproblems}
        solved = {}
        pending = set(sp['id'] for sp in subproblems)

        # Step 2: Solve subproblems in topological order with parallelization
        while pending:
            # Find independent subproblems (no unsolved dependencies)
            ready = []
            for sp_id in pending:
                deps = dependency_graph[sp_id].get('dependencies', "").split(',')
                deps = [d.strip() for d in deps if d.strip()]
                if all(d in solved for d in deps):
                    ready.append(sp_id)
            
            if not ready:
                break  # Circular dependency or error

            # Solve ready subproblems in parallel
            async def solve_subproblem(sp_id):
                sp = dependency_graph[sp_id]
                
                # Classify subproblem type
                classification = await self.generate(
                    instruction=f"""
                    Classify this subproblem for optimal solving strategy:
                    "{sp['description']}"
                    
                    Choose one: 
                    - COMPUTATIONAL: Requires precise arithmetic (use programmer)
                    - LOGICAL: Requires reasoning or assumption (use generate)
                    - VALIDATION: Requires constraint checking (use revise)
                    
                    Output only the classification word.
                    """,
                    context=""
                )
                
                if "COMPUTATIONAL" in classification.upper():
                    # Extract numbers and operations
                    context_data = await self.generate(
                        instruction=f"""
                        Extract all numerical values, units, and operations from:
                        "{sp['description']}"
                        
                        Also include any solved dependencies: {[(d, solved[d]) for d in sp.get('dependencies', "").split(',') if d.strip()]}
                        
                        Format as: "Calculate X using values A, B with operation OP"
                        """,
                        context=""
                    )
                    
                    result = await self.programmer(
                        instruction=f"""
                        Write a Python function to compute the result for: {sp['description']}
                        Context: {context_data}
                        Rules:
                        - Use only basic arithmetic operations
                        - Return a single numerical value
                        - Handle decimals appropriately
                        - Do not print, only return the number
                        """,
                        context=context_data
                    )
                    
                else:
                    # Use generate for logical subproblems
                    result = await self.generate(
                        instruction=f"""
                        Solve this subproblem through reasoning:
                        "{sp['description']}"
                        
                        Use solved dependencies: {[(d, solved[d]) for d in sp.get('dependencies', "").split(',') if d.strip()]}
                        
                        Output only the numerical result or logical conclusion.
                        If assumption is needed, state it explicitly.
                        """,
                        context=""
                    )
                
                # Validate result
                validated = await self.revise(
                    instruction=f"""
                    Validate this result: {result}
                    For subproblem: {sp['description']}
                    
                    Check:
                    - Is it non-negative? (unless context allows negative)
                    - Is it in correct units?
                    - Does it respect constraints (e.g., whole numbers for people)?
                    - Is it reasonable in real-world context?
                    
                    If invalid, explain why and provide corrected value.
                    Otherwise, return the original value unchanged.
                    """,
                    context=result
                )
                
                # Extract numerical value
                numbers = re.findall(r'-?\d+\.?\d*', validated)
                if numbers:
                    return float(numbers[0]) if '.' in numbers[0] else int(float(numbers[0]))
                return validated

            # Execute in parallel
            results = await asyncio.gather(*[solve_subproblem(sp_id) for sp_id in ready])
            
            # Update solved dictionary
            for sp_id, result in zip(ready, results):
                solved[sp_id] = result
                pending.remove(sp_id)

        # Step 3: Synthesize final answer
        synthesis_contexts = [f"Subproblem {sp_id}: {result}" for sp_id, result in solved.items()]
        
        final_answer = await self.ensemble(
            instruction="""
            Synthesize all subproblem results into a single final answer.
            Steps:
            1. Combine results in logical order (respect dependencies)
            2. Apply any remaining operations (e.g., final addition)
            3. Ensure unit consistency
            4. Round appropriately if needed (context determines precision)
            5. Output ONLY the final numerical value, nothing else.
            
            If multiple valid answers exist, choose the most contextually appropriate.
            """,
            contexts_list=synthesis_contexts
        )

        # Step 4: Meta-cognitive sanity check
        sanity_check = await self.generate(
            instruction=f"""
            Perform a sanity check on final answer: {final_answer}
            
            Questions:
            - Is the magnitude reasonable? (e.g., not millions for a sandwich order)
            - Does it match real-world expectations?
            - Are there any obvious calculation errors?
            
            If answer fails sanity check, output "RETRY" followed by reason.
            Otherwise, output "VALID".
            """,
            context=""
        )

        if "RETRY" in sanity_check.upper():
            # Simple fallback: try direct programmer approach
            direct_solution = await self.programmer(
                instruction="""
                Solve the entire problem directly with Python code.
                Extract all numbers and relationships from the original problem.
                Perform calculations step by step.
                Return only the final numerical answer.
                """,
                context=""
            )
            
            # Extract number from direct solution
            numbers = re.findall(r'-?\d+\.?\d*', direct_solution)
            if numbers:
                final_answer = numbers[0]

        # Final extraction and cleanup
        numbers = re.findall(r'-?\d+\.?\d*', str(final_answer))
        if numbers:
            result = float(numbers[0])
            # Convert to int if whole number
            if result.is_integer():
                return int(result)
            return result
        
        return final_answer