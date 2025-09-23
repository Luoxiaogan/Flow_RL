# Workflow ID: mbppplus_37_0
# Benchmark: mbppplus
# Data Indices: [11, 105, 312]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving.
        Dynamically classifies problem type, generates parallel solutions,
        validates for edge cases, and synthesizes optimal answer.
        """
        import asyncio
        import re

        # PHASE 1: Problem Classification & Structural Decomposition
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze this programming problem:
            1. Classify the primary problem type (list/tuple manipulation, set operations, string pattern matching, mathematical computation, logical validation)
            2. Identify expected input and output data structures (list, tuple, set, string, boolean, etc.)
            3. List critical edge cases to handle (empty inputs, single elements, duplicates, type boundaries)
            4. Suggest 2-3 applicable algorithmic approaches (e.g., zip for transposition, set for membership, regex for patterns)
            5. Note any constraints on order preservation, mutability, or side effects
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (3 strategies)
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a direct, imperative solution:
                Problem Analysis: {problem_analysis}
                
                Approach:
                - Use explicit loops and conditionals
                - Handle edge cases identified above
                - Maintain exact output type specified
                - Include comments explaining key steps
                - Prioritize clarity over brevity
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a functional/Pythonic solution:
                Problem Analysis: {problem_analysis}
                
                Approach:
                - Use built-in functions (zip, map, filter, set, any, all, comprehensions)
                - Leverage Python's expressive syntax
                - Handle edge cases identified above
                - Maintain exact output type specified
                - Prioritize elegance and efficiency
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a pattern-matching or declarative solution:
                Problem Analysis: {problem_analysis}
                
                Approach:
                - If string-related, consider regex or string methods
                - If set-related, use set operations
                - If mathematical, use arithmetic or itertools
                - Handle edge cases identified above
                - Maintain exact output type specified
                - Prioritize robustness and generality
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            )
        ]
        
        # Execute all strategies in parallel
        raw_solutions = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Solution Validation & Refinement
        validation_tasks = []
        for i, solution in enumerate(raw_solutions):
            validation_tasks.append(
                self.revise(
                    instruction=f"""Critically revise this solution:
                    Problem Analysis: {problem_analysis}
                    
                    Revision Criteria:
                    1. Does it handle ALL edge cases mentioned in analysis? (empty inputs, single elements, etc.)
                    2. Does it preserve required data types and structure? (list vs tuple vs set)
                    3. Is the logic correct for both typical and boundary cases?
                    4. Are there any off-by-one errors or indexing mistakes?
                    5. Is the code defensively written (graceful error handling)?
                    6. Can efficiency be improved without sacrificing correctness?
                    
                    Return ONLY the corrected function implementation, nothing else.""",
                    context=solution
                )
            )
        
        # Execute all validations in parallel
        refined_solutions = await asyncio.gather(*validation_tasks)

        # PHASE 4: Ensemble Synthesis & Final Selection
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the optimal solution:
            Evaluation Criteria:
            1. Correctness: Must handle all edge cases and produce exact expected output type
            2. Robustness: Graceful handling of unexpected inputs
            3. Efficiency: Reasonable time/space complexity
            4. Readability: Clear, maintainable code
            5. Pythonic: Uses appropriate built-ins and idioms
            
            If multiple solutions are equally valid, prefer the most concise and Pythonic.
            If no solution is perfect, synthesize a hybrid that combines their strengths.
            Return ONLY the final function implementation with necessary imports, nothing else.""",
            contexts_list=refined_solutions
        )

        return final_solution