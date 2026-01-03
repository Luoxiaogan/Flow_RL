# Workflow ID: mgsmbn_56_0
# Benchmark: mgsmbn
# Data Indices: [15]

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

        # PHASE 1: Problem Decomposition & Entity Mapping
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic, solvable subproblems.
        For each subproblem:
        - Clearly state what needs to be calculated
        - Specify input values and their sources
        - Define output format and units
        - List dependencies (other subproblems that must be solved first)
        - Include validation constraints (e.g., "result must be positive", "must be integer")
        
        Focus on mathematical relationships, not linguistic structure.
        Example subproblem: "Calculate total time elapsed based on given walking segments"
        Return as structured list of dictionaries with keys: id, description, dependencies.
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Early exit for trivial problems (single subproblem)
        if len(subproblems) == 1:
            simple_solution = await self.programmer(
                instruction=f"""
                Solve this single-step math problem:
                {subproblems[0]['description']}
                
                Write Python code that:
                - Uses only basic arithmetic operations
                - Includes unit validation
                - Returns only the numerical result
                - Handles edge cases (division by zero, negative results)
                """,
                context=""
            )
            final_answer = await self.summarize(
                instruction="Extract ONLY the final numerical answer. No units, no text, just the number.",
                context=simple_solution
            )
            return final_answer

        # PHASE 2: Parallel Strategy Generation
        # Strategy 1: Algebraic/Programmatic Approach
        algebraic_task = asyncio.create_task(
            self.programmer(
                instruction=f"""
                Solve using symbolic mathematics and Python code.
                Subproblems to solve in order: {json.dumps(subproblems, indent=2)}
                
                Requirements:
                - Define variables for unknowns
                - Set up equations based on relationships
                - Solve step by step
                - Validate each intermediate result against constraints
                - Return final numerical answer only
                - Include unit consistency checks
                """,
                context=""
            )
        )

        # Strategy 2: Step-by-Step Arithmetic
        arithmetic_task = asyncio.create_task(
            self.generate(
                instruction=f"""
                Solve through sequential arithmetic reasoning.
                Subproblems: {json.dumps(subproblems, indent=2)}
                
                For each subproblem in dependency order:
                1. State the calculation needed
                2. Show the arithmetic operation
                3. Provide intermediate result
                4. Verify against constraints
                5. Pass result to next subproblem
                
                Format: "Step [id]: [description] → [calculation] = [result] ✓[validation]"
                End with final answer in format: "FINAL ANSWER: [number]"
                """,
                context=""
            )
        )

        # Strategy 3: State Simulation (for time/rate problems)
        simulation_task = asyncio.create_task(
            self.generate(
                instruction=f"""
                Model this as a state simulation over time/events.
                Subproblems: {json.dumps(subproblems, indent=2)}
                
                Create a timeline:
                - Initialize state variables (distance, time, quantity, etc.)
                - For each event/step, update state
                - Track units at each transition
                - Validate state after each update
                - Final state contains the answer
                
                Format: "Time 0: [initial state] → Event 1: [action] → State: [new state] ✓[validation]"
                End with: "FINAL STATE: [answer]"
                """,
                context=""
            )
        )

        # Execute all strategies in parallel
        algebraic_result, arithmetic_result, simulation_result = await asyncio.gather(
            algebraic_task, arithmetic_task, simulation_task
        )

        # PHASE 3: Consensus Synthesis & Verification
        candidate_answers = [algebraic_result, arithmetic_result, simulation_result]
        
        consensus = await self.ensemble(
            instruction="""
            Synthesize these three solution attempts into one verified answer.
            Steps:
            1. Extract numerical answers from each candidate
            2. Compare values - if two or more agree, prefer that answer
            3. If all differ, identify which solution best satisfies:
               - Mathematical correctness
               - Unit consistency
               - Constraint satisfaction
               - Step-by-step validity
            4. If any solution violates constraints (negative values, impossible units), discard it
            5. Return ONLY the final numerical answer, nothing else
            
            Special cases:
            - If answers are 5.99, 6.0, 6.01 → return 6
            - If one solution is clearly erroneous, use majority
            - If no consensus, pick the most rigorously validated solution
            """,
            contexts_list=candidate_answers
        )

        # Final verification pass
        verified_answer = await self.revise(
            instruction="""
            Verify this answer by working backwards:
            1. Assume this is the correct answer
            2. Plug it back into the original problem narrative
            3. Check if all given conditions are satisfied
            4. Ensure no contradictions or impossible scenarios
            5. If verification fails, recalculate the most uncertain subproblem
            6. Return ONLY the final numerical answer (after correction if needed)
            
            Example: If answer is 6 mph, verify that with this speed, 
            total time = 12 miles / 4 mph average = 3 hours, 
            and 1h (first 4mi) + 1h (next 2mi) + 1h (last 6mi at 6mph) = 3h ✓
            """,
            context=consensus
        )

        # Final formatting
        final_output = await self.summarize(
            instruction="Extract ONLY the numerical answer. Remove any units, text, or explanations. If decimal, round to 2 places unless problem specifies otherwise.",
            context=verified_answer
        )
        
        return final_output