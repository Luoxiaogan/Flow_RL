# Workflow ID: mgsmbn_76_0
# Benchmark: mgsmbn
# Data Indices: [32]

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

        # PHASE 1: DECOMPOSE & CLASSIFY
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic subproblems.
        For each subproblem:
        - Identify WHAT needs to be calculated or determined
        - Specify any dependencies (which other subproblems must be solved first)
        - Classify its type: [Sequential, Proportional, Distribution, Comparison, UnitConversion, ConstraintCheck]
        - Extract all relevant numbers and their semantic roles (e.g., "250" = "calories per serving")
        
        Format each subproblem as:
        ID: [unique_id]
        Description: [clear task description]
        Dependencies: [comma-separated IDs or "none"]
        Type: [classification]
        Entities: [key numbers/units with meanings]
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: PARALLEL SOLVE & REVISE (per subproblem)
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            sp_type = subproblem['type']
            sp_entities = subproblem['entities']
            
            # Generate multiple solution approaches based on type
            generate_instruction = f"""
            Solve this subproblem using {sp_type} reasoning:
            "{sp_desc}"
            
            Entities: {sp_entities}
            
            Generate 2 distinct solution approaches:
            Approach A: Direct calculation path
            Approach B: Alternative method (e.g., algebraic, proportional, unit analysis)
            
            For each approach:
            - Show step-by-step reasoning
            - Explicitly state any assumptions
            - Highlight potential pitfalls
            """
            
            initial_solutions = await self.generate(
                instruction=generate_instruction,
                context=""
            )
            
            # Revise for clarity and correctness
            revise_instruction = """
            Critically revise the solutions above:
            - Fix any mathematical errors
            - Clarify ambiguous steps
            - Add missing unit tracking
            - Flag any assumptions that might not hold
            - Ensure real-world constraints are respected (no negative quantities, etc.)
            Output only the revised, improved version.
            """
            
            revised_solution = await self.revise(
                instruction=revise_instruction,
                context=initial_solutions
            )
            
            return {
                'id': sp_id,
                'solution': revised_solution,
                'type': sp_type
            }

        # Solve all independent subproblems in parallel
        subproblem_tasks = [solve_subproblem(sp) for sp in subproblems if sp['dependencies'] == 'none']
        solved_subproblems = await asyncio.gather(*subproblem_tasks)
        
        # Handle dependent subproblems sequentially (simplified for brevity)
        # In full implementation, you'd resolve dependencies topologically
        for sp in subproblems:
            if sp['dependencies'] != 'none':
                # Would integrate results from dependencies here
                pass

        # PHASE 3: ENSEMBLE & VALIDATE
        ensemble_instruction = """
        You are given multiple solved subproblems. Synthesize them into a complete, coherent solution:
        - Ensure chronological/logical flow matches problem narrative
        - Verify that outputs of earlier subproblems correctly feed into later ones
        - Cross-check unit consistency (e.g., grams, calories, hours)
        - Flag any remaining inconsistencies or gaps
        
        Output the complete solution narrative with final answer highlighted.
        """
        
        synthesized_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[sp['solution'] for sp in solved_subproblems]
        )

        # PHASE 4: COMPUTE & VERIFY
        compute_instruction = f"""
        Based on this synthesized solution:
        "{synthesized_solution}"
        
        Generate Python code to compute the final numerical answer.
        Requirements:
        - Use exact arithmetic (no floating point unless necessary)
        - Include unit conversions if needed
        - Validate against constraints (e.g., non-negative, integer if required)
        - Output ONLY the final number (no text, no units)
        
        Example structure: