# Workflow ID: limr_35_0
# Benchmark: limr
# Data Indices: [88, 153]

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

        # Step 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Include:
            1. Primary mathematical domain (e.g., number theory, combinatorics, algebra, geometry, trigonometry)
            2. Key variables, constraints, and invariants
            3. Expected answer format (integer, expression, etc.) and range if applicable
            4. At least three distinct solution strategies with brief rationale for each
            5. Any relevant theorems, identities, or mathematical principles that might apply
            6. Potential pitfalls or common mistakes to avoid
            Format as a structured JSON-like object with keys: domain, constraints, answer_format, strategies, theorems, pitfalls""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Based on the problem classification:
            {classification}
            
            Decompose the problem into a sequence of interdependent subproblems. Each subproblem should be:
            - Atomic and clearly defined
            - Have explicit dependencies on previous subproblems
            - Progress toward the final solution
            - Include any necessary intermediate calculations or proofs
            
            Return as a list of subproblems with 'id', 'description', and 'dependencies' fields.""",
            context=classification
        )

        # Step 3: Parallel Solution Exploration
        # Generate multiple solution attempts for each subproblem or overall problem
        solution_attempts = []
        
        # Strategy 1: Direct Mathematical Reasoning
        attempt1 = await self.generate(
            instruction=f"""Using the problem classification and decomposition, solve the problem through direct mathematical reasoning.
            - Show all steps clearly
            - Justify each transformation or assumption
            - Highlight key insights or non-obvious steps
            - Verify intermediate results where possible
            Classification: {classification}
            Decomposition: {json.dumps(decomposition)}""",
            context=""
        )
        solution_attempts.append(attempt1)

        # Strategy 2: Algorithmic/Computational Approach
        attempt2 = await self.programmer(
            instruction=f"""Implement a computational solution to the problem. Consider:
            - Efficient algorithms or data structures
            - Boundary conditions and edge cases
            - Precision requirements (exact integer output)
            - Smart pruning or early termination where applicable
            Classification: {classification}
            Decomposition: {json.dumps(decomposition)}""",
            context="",
            max_retries=3
        )
        solution_attempts.append(attempt2)

        # Strategy 3: Proof-Based or Theorem-Driven Approach
        attempt3 = await self.generate(
            instruction=f"""Solve the problem by applying formal mathematical theorems or proof techniques.
            - Reference relevant theorems from classification
            - Use proof by contradiction, induction, or other formal methods if applicable
            - Structure as a formal mathematical proof
            - Conclude with the exact answer required
            Classification: {classification}
            Decomposition: {json.dumps(decomposition)}""",
            context=""
        )
        solution_attempts.append(attempt3)

        # Step 4: Ensemble Synthesis
        synthesized_solution = await self.ensemble(
            instruction="""Evaluate the three solution attempts and synthesize the best possible solution. Consider:
            - Mathematical correctness and rigor
            - Completeness of steps and justification
            - Adherence to problem constraints
            - Clarity and precision of final answer
            - Efficiency and elegance of approach
            Select the best elements from each attempt or create a new synthesis that combines their strengths.
            The final answer must be an integer between 000 and 999, clearly boxed at the end.""",
            contexts_list=solution_attempts
        )

        # Step 5: Adversarial Validation Loop
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Critically validate the following solution. Look for:
                - Mathematical errors or gaps in logic
                - Unjustified assumptions
                - Arithmetic or algebraic mistakes
                - Violations of problem constraints
                - Alternative interpretations or edge cases
                If no errors are found, respond with 'VALIDATED'. Otherwise, describe all issues found.
                Solution to validate: {synthesized_solution}""",
                context=synthesized_solution
            )
            
            if "VALIDATED" in validation.upper():
                break
            else:
                synthesized_solution = await self.revise(
                    instruction=f"""Revise the solution to fix all issues identified in validation:
                    Validation feedback: {validation}
                    Ensure the revised solution is mathematically rigorous and produces the correct integer answer.""",
                    context=synthesized_solution
                )

        # Step 6: Final Answer Extraction
        final_answer = await self.programmer(
            instruction="""Extract the final integer answer from the solution text. The answer should be:
            - An integer between 000 and 999
            - Clearly identified in the solution (often boxed or explicitly stated)
            - If multiple answers exist, select the one specified by the problem (e.g., largest, smallest)
            - Return only the integer, no explanation
            Solution text: """ + synthesized_solution,
            context=synthesized_solution,
            max_retries=3
        )

        # Clean and return final answer
        # Extract digits only
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if match:
            return match.group(0).zfill(3)  # Ensure 3-digit format
        else:
            # Fallback: return first 3 digits found or default
            digits = re.findall(r'\d', final_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            elif len(digits) > 0:
                return ''.join(digits).zfill(3)
            else:
                return "000"  # Ultimate fallback