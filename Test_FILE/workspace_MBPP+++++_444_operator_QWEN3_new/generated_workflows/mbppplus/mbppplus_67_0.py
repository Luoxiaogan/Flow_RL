# Workflow ID: mbppplus_67_0
# Benchmark: mbppplus
# Data Indices: [253, 180, 332]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import math
        import heapq

        # PHASE 1: PARALLEL SOLUTION HYPOTHESIS GENERATION
        # Generate three independent solution approaches from different perspectives
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction="""You are an expert Python programmer. Analyze the problem and implement the most direct, 
                idiomatic solution. Focus on using built-in functions and standard library modules. 
                Assume inputs are well-formed but include basic edge case handling (empty inputs, single elements).
                Return ONLY the function implementation with necessary imports, nothing else.
                Think step by step: What is the core transformation? What Python tools are best suited?
                Example: For heap problems, use heapq.heapify; for string problems, consider regex or string methods.""",
                context=""
            ),
            self.generate(
                instruction="""You are a mathematical/logical analyst. Break down the problem into first principles.
                What are the underlying mathematical operations or logical rules? 
                Implement a solution from scratch without relying on specialized libraries.
                Handle edge cases explicitly: zero, negative numbers, empty sequences, duplicates.
                Return ONLY the function implementation with necessary imports, nothing else.
                Think: What invariants must be preserved? What are the boundary conditions?""",
                context=""
            ),
            self.generate(
                instruction="""You are a defensive programming specialist. Implement the solution with maximum robustness.
                Add explicit type checks, input validation, and comprehensive edge case handling.
                Consider: empty inputs, None values, extreme values, malformed data.
                Use try-except blocks if appropriate. Document edge case handling in comments.
                Return ONLY the function implementation with necessary imports, nothing else.
                Think: What could go wrong? How would this fail in production?""",
                context=""
            )
        )

        # PHASE 2: ADVERSARIAL REVISION - Each solution critiques itself
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""You are now a critical code reviewer. Assume this solution has a hidden flaw.
                Find the edge case it doesn't handle, the assumption it wrongly makes, or the requirement it misses.
                Revise the code to fix this flaw. Add comments explaining the edge case you fixed.
                If no flaw is found, strengthen the solution with additional validation or clearer logic.
                Return ONLY the revised function implementation, nothing else.
                Think: What input would break this? What does the problem description imply but not state?""",
                context=sol
            ) for sol in solution_hypotheses]
        )

        # PHASE 3: ENSEMBLE SYNTHESIS - Combine the best elements
        synthesized_solution = await self.ensemble(
            instruction="""You are synthesizing a final, production-ready solution from multiple candidates.
            Combine the strongest elements from each: use the most elegant core logic, the most comprehensive edge case handling,
            and the clearest structure. Add comments explaining key decisions and edge case handling.
            Ensure the solution matches the exact function signature and return type specified.
            Handle ALL edge cases: empty inputs, single elements, duplicates, type boundaries.
            Return ONLY the final function implementation with necessary imports, nothing else.
            Think: What makes each solution strong? How can they complement each other? What edge cases are still unhandled?""",
            contexts_list=revised_solutions
        )

        # PHASE 4: VALIDATION LOOP - Generate test cases to stress-test the solution
        validation_test_cases = await self.generate(
            instruction=f"""You are a QA engineer. Given this solution, generate three test cases that would expose flaws:
            1. A normal case (typical input)
            2. A boundary case (edge of input domain)
            3. A malicious case (unexpected input format or extreme value)
            Format as Python assert statements. Think: What input would this solution handle poorly?""",
            context=synthesized_solution
        )

        # PHASE 5: FINAL REVISION BASED ON VALIDATION
        final_solution = await self.revise(
            instruction=f"""Revise the solution to handle the edge cases revealed by these test cases:
            {validation_test_cases}
            Strengthen input validation, add missing edge case handling, or adjust logic as needed.
            Keep the solution clean and efficient. Return ONLY the final function implementation, nothing else.
            Think: How can I modify the code to pass all these tests without overcomplicating it?""",
            context=synthesized_solution
        )

        return final_solution