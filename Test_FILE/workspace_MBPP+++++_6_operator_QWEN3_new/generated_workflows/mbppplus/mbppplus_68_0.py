# Workflow ID: mbppplus_68_0
# Benchmark: mbppplus
# Data Indices: [308, 146]

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

        # Phase 1: Problem Classification and Strategy Extraction
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it for optimal solution strategy. Consider:

1. Problem Category: Is this primarily about:
   - String manipulation (palindromes, parsing, formatting)
   - Dynamic programming (LCS, knapsack, optimal substructure)
   - Mathematical computation (number theory, sequences, arithmetic)
   - Data structure operations (searching, sorting, set operations)
   - Logical validation (conditions, comparisons, edge cases)

2. Algorithmic Pattern: What core algorithmic approach is most suitable?
   - Brute force with early termination
   - Dynamic programming (1D, 2D, 3D)
   - Greedy strategy
   - Two-pointer technique
   - Mathematical formula derivation
   - Recursive backtracking
   - Other (specify)

3. Edge Cases: What boundary conditions must be handled?
   - Empty inputs
   - Single element cases
   - Zero or negative values
   - Duplicate elements
   - Maximum/minimum value boundaries

4. Implementation Strategy: Recommend specific implementation approach including:
   - Data structures to use
   - Loop structures or recursion
   - Key variables to track
   - Potential optimizations

5. Test Cases: Generate 3-5 critical test cases including edge cases that must pass.

Provide structured analysis with clear sections for each point above.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation with Different Emphases
        solution_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Implement a solution based on this strategy analysis:
{classification}

Focus on: MAXIMUM CORRECTNESS
- Handle ALL edge cases mentioned in analysis
- Include detailed comments explaining logic
- Add assert statements for critical test cases identified
- Prioritize correctness over performance
- Return exactly the required data type""",
                context=classification
            ),
            self.programmer(
                instruction=f"""Implement a solution based on this strategy analysis:
{classification}

Focus on: OPTIMAL EFFICIENCY
- Use most efficient algorithm possible
- Minimize time/space complexity
- Consider mathematical shortcuts or optimizations
- Still handle all edge cases
- Clean, concise code with good variable names""",
                context=classification
            ),
            self.programmer(
                instruction=f"""Implement a solution based on this strategy analysis:
{classification}

Focus on: ROBUST ERROR HANDLING
- Assume inputs could be malformed
- Add defensive checks where appropriate
- Handle edge cases with explicit conditions
- Include comprehensive test assertions
- Write code that fails gracefully if assumptions are violated""",
                context=classification
            )
        )

        # Phase 3: Ensemble Synthesis of Best Solution
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best possible solution from these three attempts. Consider:

1. Correctness: Which solution handles edge cases most thoroughly?
2. Efficiency: Which has the best time/space complexity?
3. Clarity: Which is most readable and maintainable?
4. Robustness: Which has the best error handling and defensive programming?

Create a merged solution that:
- Takes the core algorithm from the most correct implementation
- Incorporates optimizations from the most efficient version
- Adds robustness features from the defensive version
- Uses clear variable names and comments
- Includes critical test assertions
- Returns exactly the required data type

Output ONLY the final Python function implementation with imports if needed.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Adversarial Revision (Assume it's wrong and fix it)
        refined_solution = await self.revise(
            instruction="""Assume this code is subtly wrong. Perform adversarial code review:

1. Line-by-line critique: What could be wrong with each line?
2. Edge case testing: Does it handle empty inputs, boundaries, zeros, duplicates?
3. Off-by-one errors: Check all loops and array/string indices
4. Type consistency: Are return types and variable types correct?
5. Logic flaws: Are there any conditions that could fail?
6. Performance traps: Any unnecessary computations or memory usage?

Rewrite the code to fix ALL potential issues. Make it bulletproof.
Output ONLY the corrected Python function implementation.""",
            context=synthesized_solution
        )

        # Phase 5: Final Ensemble (in case revision changed core logic)
        final_solution = await self.ensemble(
            instruction="""Compare the synthesized and revised solutions. The revised version may have fixed bugs but potentially introduced new issues or lost optimizations.

Create the final solution that:
- Maintains all bug fixes from revision
- Preserves key optimizations from synthesis
- Is maximally robust and correct
- Follows all problem requirements exactly
- Returns the precise required data type

Output ONLY the final Python function implementation with necessary imports.""",
            contexts_list=[synthesized_solution, refined_solution]
        )

        return final_solution