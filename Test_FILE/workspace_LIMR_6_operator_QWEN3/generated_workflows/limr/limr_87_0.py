# Workflow ID: limr_87_0
# Benchmark: limr
# Data Indices: [224, 120]

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

        # STEP 1: Generate multiple problem decompositions in parallel
        decomposition_attempts = await asyncio.gather(
            self.decompose(
                instruction="""Break this problem into the most mathematically natural subproblems. 
                Focus on logical dependencies and prerequisite knowledge. 
                Each subproblem should be solvable independently given its dependencies. 
                Prioritize clarity and mathematical coherence over minimalism.""",
                context=""
            ),
            self.decompose(
                instruction="""Break this problem into subproblems optimized for computational solving. 
                Identify which parts can be calculated numerically, which require symbolic manipulation, 
                and which need theoretical insight. Structure dependencies to enable parallel computation 
                where possible.""",
                context=""
            ),
            self.decompose(
                instruction="""Break this problem into subproblems by mathematical domain: 
                separate geometric, algebraic, combinatorial, and number-theoretic components. 
                Clearly label each subproblem with its domain and required techniques. 
                Dependencies should reflect conceptual prerequisites, not just computational order.""",
                context=""
            )
        )

        # STEP 2: Ensemble select the best decomposition
        selected_decomposition = await self.ensemble(
            instruction="""Evaluate these three decompositions of the same problem. 
            Select the one that is:
            1. Most complete (covers all aspects of the problem)
            2. Most coherent (subproblems logically connect)
            3. Most solvable (each subproblem is clearly defined and tractable)
            4. Best structured for verification and error-checking
            Return only the selected decomposition, no commentary.""",
            contexts_list=[str(d) for d in decomposition_attempts]
        )

        # STEP 3: Extract subproblem IDs for processing
        subproblem_ids = []
        if isinstance(selected_decomposition, list):
            subproblem_ids = [sp['id'] for sp in selected_decomposition]
        else:
            # Fallback: attempt to parse if returned as string
            lines = selected_decomposition.split('\n')
            for line in lines:
                if 'id:' in line.lower() or '"id"' in line:
                    match = re.search(r'[\'"]id[\'"]\s*[:=]\s*[\'"]([^\'"]+)[\'"]', line)
                    if match:
                        subproblem_ids.append(match.group(1))

        # STEP 4: Solve each subproblem in parallel with domain-specific strategies
        subproblem_solutions = {}
        subproblem_tasks = []

        for sp_id in subproblem_ids:
            task = asyncio.create_task(self.solve_subproblem(sp_id, selected_decomposition))
            subproblem_tasks.append(task)

        solutions = await asyncio.gather(*subproblem_tasks)
        
        for i, sp_id in enumerate(subproblem_ids):
            subproblem_solutions[sp_id] = solutions[i]

        # STEP 5: Revise each solution with cross-validation
        revised_solutions = {}
        revision_tasks = []

        for sp_id, solution in subproblem_solutions.items():
            task = asyncio.create_task(
                self.revise(
                    instruction=f"""Critically revise this solution for subproblem {sp_id}:
                    1. Verify all mathematical steps for correctness
                    2. Check consistency with dependencies (if any)
                    3. Ensure alignment with original problem constraints
                    4. Confirm that the answer format matches requirements
                    5. Look for any hidden assumptions or edge cases
                    Improve clarity, add missing justifications, and fix any errors.""",
                    context=solution
                )
            )
            revision_tasks.append(task)

        revised_list = await asyncio.gather(*revision_tasks)
        for i, sp_id in enumerate(subproblem_ids):
            revised_solutions[sp_id] = revised_list[i]

        # STEP 6: Synthesize final answer
        synthesis_context = "\n\n".join([f"Subproblem {sp_id}: {sol}" for sp_id, sol in revised_solutions.items()])
        
        synthesized_answer = await self.generate(
            instruction=f"""Synthesize a complete, coherent solution from these revised subproblem solutions:
            {synthesis_context}
            
            Your task:
            1. Integrate all subproblem solutions into a unified whole
            2. Ensure logical flow between steps
            3. Highlight the final numerical answer (must be integer 000-999)
            4. Double-check that all original problem constraints are satisfied
            5. Present the answer in the required format""",
            context=synthesis_context
        )

        # STEP 7: Extract and verify final answer with programmer
        final_answer = await self.programmer(
            instruction="""Extract the final numerical answer from the solution text. 
            The answer must be an integer between 000 and 999. 
            If multiple candidates exist, select the one that best satisfies all problem constraints. 
            If no clear answer, return 000. 
            Validate by checking against key constraints from the original problem.""",
            context=synthesized_answer
        )

        # STEP 8: Final summarization and formatting
        final_output = await self.summarize(
            instruction="""Condense to the final answer only. 
            Must be exactly three digits (000-999). 
            Remove all text, explanations, and units. 
            If the answer is a single or double digit, pad with leading zeros.
            Example: if answer is 42, output '042'""",
            context=final_answer
        )

        # Extract just the 3-digit number
        match = re.search(r'\b(\d{3})\b', final_output)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and pad
            numbers = re.findall(r'\d+', final_output)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"{num:03d}"
            else:
                return "000"

    async def solve_subproblem(self, subproblem_id, decomposition):
        """Solve a single subproblem with appropriate strategy"""
        # Get subproblem description
        subproblem_desc = ""
        if isinstance(decomposition, list):
            for sp in decomposition:
                if sp.get('id') == subproblem_id:
                    subproblem_desc = sp.get('description', '')
                    break
        
        # Classify subproblem type
        classification = await self.generate(
            instruction=f"""Classify this subproblem for optimal solving strategy:
            Subproblem: {subproblem_desc}
            
            Classify as one of:
            - COMPUTATIONAL: Requires numerical calculation, equation solving, or algorithmic processing
            - THEORETICAL: Requires proof, logical deduction, or conceptual insight
            - HYBRID: Requires both computation and theoretical reasoning
            
            Also identify:
            - Key mathematical domain (geometry, algebra, combinatorics, etc.)
            - Required techniques or theorems
            - Potential pitfalls or edge cases""",
            context=subproblem_desc
        )

        # Route to appropriate solving strategy
        if "COMPUTATIONAL" in classification.upper() or "HYBRID" in classification.upper():
            # Use programmer for computational aspects
            solution = await self.programmer(
                instruction=f"""Solve this subproblem using Python code:
                {subproblem_desc}
                
                Classification context: {classification}
                
                Requirements:
                - Generate complete, self-contained code
                - Include all necessary imports
                - Show all steps of calculation
                - Verify results against constraints
                - Return final answer with clear labeling""",
                context=subproblem_desc
            )
        else:
            # Use generate for theoretical aspects
            solution = await self.generate(
                instruction=f"""Solve this theoretical subproblem with rigorous mathematical reasoning:
                {subproblem_desc}
                
                Classification context: {classification}
                
                Requirements:
                - Show all logical steps
                - Justify each assertion
                - Reference relevant theorems or principles
                - Consider edge cases and special conditions
                - Present clear, final conclusion""",
                context=subproblem_desc
            )
        
        return solution