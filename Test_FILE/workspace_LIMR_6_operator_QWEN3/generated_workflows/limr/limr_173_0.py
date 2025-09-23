# Workflow ID: limr_173_0
# Benchmark: limr
# Data Indices: [73, 83]

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

        # PHASE 1: STRATEGIC DECOMPOSITION
        decomposition_instruction = """
        Analyze the problem and decompose it into distinct mathematical strategy branches.
        Each subproblem should represent a different high-level approach (e.g., algebraic manipulation, 
        combinatorial counting, geometric interpretation, optimization via calculus, number theory).
        For each approach, specify:
        - The mathematical domain it belongs to
        - Key insights or theorems it might leverage
        - Potential pitfalls or constraints to watch for
        Format as structured subproblems with minimal dependencies.
        """
        decomposition = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_tasks = []
        for i, subproblem in enumerate(decomposition):
            strategy_id = subproblem.get('id', f'strategy_{i}')
            strategy_desc = subproblem.get('description', '')
            
            strategy_instruction = f"""
            Develop a complete solution approach for this mathematical strategy:
            Strategy ID: {strategy_id}
            Description: {strategy_desc}
            
            Steps to follow:
            1. Formalize the mathematical setup (variables, constraints, objective)
            2. Apply relevant theorems or techniques from the specified domain
            3. Show key derivations or transformations
            4. Identify potential failure points or assumptions
            5. Propose how to compute or derive the final integer answer
            
            Be rigorous, detailed, and explicit about every step.
            """
            task = self.generate(instruction=strategy_instruction, context="")
            strategy_tasks.append(task)
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # PHASE 3: META-VALIDATION OF EACH STRATEGY
        validation_tasks = []
        for i, strategy_result in enumerate(strategy_results):
            validation_instruction = f"""
            Critically evaluate this solution strategy:
            
            {strategy_result}
            
            Validation checklist:
            - Are all problem constraints respected?
            - Are mathematical operations justified and correct?
            - Are there any logical gaps or unsupported assumptions?
            - Does the approach lead to a computable integer answer?
            - What are the most likely sources of error?
            
            If the strategy is flawed, explain why and suggest how to fix it.
            If it's sound, strengthen the justification and flag it as viable.
            """
            task = self.revise(instruction=validation_instruction, context=strategy_result)
            validation_tasks.append(task)
        
        validated_strategies = await asyncio.gather(*validation_tasks)

        # PHASE 4: COMPUTATIONAL GROUNDING
        computation_tasks = []
        for i, validated_strategy in enumerate(validated_strategies):
            if "flawed" in validated_strategy.lower() or "error" in validated_strategy.lower():
                continue  # Skip clearly invalid approaches
                
            computation_instruction = f"""
            Based on this validated mathematical strategy:
            
            {validated_strategy}
            
            Generate Python code to compute the exact integer answer.
            Requirements:
            - Define all necessary variables and functions
            - Implement the mathematical logic precisely
            - Handle edge cases and constraints
            - Output only the final integer answer (000-999 format)
            - Include comments explaining key steps
            - If symbolic computation is needed, use sympy
            - If optimization, use scipy or direct calculation
            """
            task = self.programmer(instruction=computation_instruction, context=validated_strategy)
            computation_tasks.append(task)
        
        computation_results = await asyncio.gather(*computation_tasks)

        # PHASE 5: ENSEMBLE SYNTHESIS & CONFLICT RESOLUTION
        if not computation_results or all("error" in r.lower() for r in computation_results):
            # Fallback: try lateral thinking approach
            lateral_instruction = """
            Previous approaches failed. Attempt a radically different perspective:
            - Look for invariants, symmetries, or hidden patterns
            - Consider extreme cases or small examples
            - Transform the problem into an equivalent but simpler form
            - Use generating functions, recursive relations, or probabilistic methods
            Derive the answer through creative insight rather than brute force.
            """
            lateral_result = await self.generate(instruction=lateral_instruction, context="")
            computation_results = [lateral_result]

        ensemble_instruction = """
        You are given multiple candidate solutions to a mathematical competition problem.
        Your task:
        1. Compare all solutions for consistency and rigor
        2. If they agree on an answer, select it and explain why it's robust
        3. If they conflict, analyze the divergence:
           - Which approach has the fewest assumptions?
           - Which respects all constraints most carefully?
           - Which has the most watertight logic?
        4. Select the single best answer (integer 000-999)
        5. Justify your selection with mathematical reasoning
        
        Format: "ANSWER: XXX" followed by detailed justification.
        """
        ensemble_result = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=computation_results
        )

        # PHASE 6: COUNTERFACTUAL STRESS TEST
        stress_instruction = f"""
        Assume the following answer is WRONG:
        
        {ensemble_result}
        
        Your task:
        1. Identify the most plausible error that could lead to this answer
        2. Re-solve the problem while actively avoiding that error
        3. If you get a different answer, explain why the original was wrong
        4. If you get the same answer, strengthen the justification with additional verification
        
        This is an adversarial validation - try to break the solution.
        """
        stress_test = await self.generate(instruction=stress_instruction, context=ensemble_result)

        # FINAL EXTRACTION & FORMATTING
        final_instruction = """
        Extract the final integer answer from the following text.
        The answer must be an integer between 000 and 999.
        If multiple candidates exist, choose the one with strongest justification.
        If no clear answer, return 000 as default.
        Output ONLY the three-digit integer, zero-padded if necessary.
        Example: "042", "123", "999"
        """
        final_answer = await self.generate(instruction=final_instruction, context=stress_test)
        
        # Clean and return
        import re
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if match:
            num = int(match.group())
            return f"{num:03d}"
        else:
            return "000"