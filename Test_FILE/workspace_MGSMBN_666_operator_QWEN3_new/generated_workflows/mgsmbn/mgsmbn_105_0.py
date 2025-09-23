# Workflow ID: mgsmbn_105_0
# Benchmark: mgsmbn
# Data Indices: [116, 39]

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

        # Step 1: Classify problem type to guide decomposition strategy
        problem_classification = await self.generate(
            instruction="""Analyze this Bengali word problem and classify it into one primary type:
            - Sequential Operations (multiple steps in order)
            - Rate Problems (speed/time/distance, work rates, unit prices)
            - Proportional Reasoning (ratios, percentages, fractions, scaling)
            - Distribution Problems (dividing quantities, equal sharing, remainders)
            - Comparison Problems (differences, "how many more")
            - Multi-entity Tracking (multiple people/objects with different quantities)
            
            Also identify:
            - What is the explicit question being asked?
            - What units are involved (টাকা, ঘণ্টা, মাইল, etc.)?
            - Are there any implicit constraints (e.g., no negative people, whole numbers only)?
            - What mathematical operations are likely needed?
            
            Format your response as a structured JSON-like summary with clear sections.""",
            context=""
        )

        # Step 2: Decompose into subproblems based on classification
        decomposition_instruction = f"""Based on the problem classification:
        {problem_classification}
        
        Decompose this problem into atomic, solvable subproblems. Each subproblem should:
        - Focus on one clear mathematical or logical operation
        - Have explicit inputs and expected outputs
        - Include unit tracking where relevant
        - Specify dependencies on other subproblems (if any)
        
        Prioritize extracting:
        - Known quantities with units
        - Unknown variables to solve for
        - Relationships between entities
        - Temporal or causal sequences (if applicable)
        
        Return a list of subproblems with IDs and dependencies."""
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Step 3: Solve subproblems in parallel, adapting strategy per type
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            
            # Generate initial solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve this subproblem from a Bengali math word problem:
                Subproblem ID: {sp_id}
                Description: {sp_desc}
                
                Steps to follow:
                1. Extract all numerical values and their units.
                2. Identify the mathematical operation needed (add, subtract, multiply, divide, etc.).
                3. If units are inconsistent, note required conversions.
                4. Show the calculation step-by-step.
                5. State the result with appropriate units.
                6. Verify: Does this result make sense in context? (e.g., no negative time, fractional people only if allowed)
                
                Format as: "RESULT: [value] [unit] | REASONING: [brief justification]".""",
                context=problem_classification
            )
            
            # Validate and revise if needed
            validation = await self.generate(
                instruction=f"""Critically validate this subproblem solution:
                Subproblem: {sp_desc}
                Proposed Solution: {solution_attempt}
                
                Check for:
                - Unit consistency and correctness
                - Arithmetic accuracy
                - Logical plausibility (e.g., time can't be negative, money should be positive)
                - Alignment with problem constraints
                - Clarity of reasoning
                
                If any issues, suggest specific corrections. Otherwise, output "VALID".""",
                context=solution_attempt
            )
            
            if "VALID" not in validation.upper():
                solution_attempt = await self.revise(
                    instruction=f"""Revise the solution based on this feedback:
                    Validation Feedback: {validation}
                    
                    Requirements:
                    - Fix all identified errors
                    - Maintain unit tracking
                    - Ensure step-by-step clarity
                    - Output in same format: "RESULT: ... | REASONING: ..." """,
                    context=solution_attempt
                )
            
            return {"id": sp_id, "solution": solution_attempt}

        # Solve all subproblems concurrently
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in subproblems]
        )
        
        # Create solution map for dependency resolution
        solution_map = {sol["id"]: sol["solution"] for sol in subproblem_solutions}

        # Step 4: Synthesize final answer by resolving dependencies
        synthesis_context = "\n\n".join([
            f"Subproblem {sol['id']}: {sol['solution']}"
            for sol in subproblem_solutions
        ])
        
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize the final answer from these subproblem solutions:
            {synthesis_context}
            
            Steps:
            1. Combine results according to problem dependencies.
            2. Perform any final calculations needed.
            3. Ensure unit consistency in final answer.
            4. Verify against original question: Does this answer what was asked?
            5. Output ONLY the numerical value (integer or decimal) with no units or text.
            
            Example: If answer is "140 টাকা", output "140".""",
            context=synthesis_context
        )

        # Step 5: Final validation and extraction
        final_answer = await self.revise(
            instruction="""Extract ONLY the numerical answer from the text below.
            - Remove all units, labels, and explanatory text.
            - If multiple numbers, select the one that answers the main question.
            - If no clear number, return "0".
            - Output must be a single integer or decimal number.
            
            Example inputs and outputs:
            Input: "The answer is 140 টাকা" → Output: "140"
            Input: "RESULT: 5.5 hours" → Output: "5.5"
            Input: "After calculation, we get 123.456" → Output: "123.456" """,
            context=final_answer_draft
        )

        # Clean and return final numerical answer
        # Extract number using regex to handle edge cases
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            return "0"