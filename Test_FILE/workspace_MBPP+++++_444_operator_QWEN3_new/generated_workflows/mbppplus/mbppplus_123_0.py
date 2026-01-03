# Workflow ID: mbppplus_123_0
# Benchmark: mbppplus
# Data Indices: [360, 149, 204]

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

        # Step 1: Deep problem analysis - understand structure, edge cases, and requirements
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Structure your response as follows:

1. Problem Classification: Is this primarily a parsing, transformation, aggregation, or validation problem? What domain does it belong to?
2. Input/Output Specification: What are the exact types and structures of inputs and expected outputs? Note any constraints.
3. Edge Cases: List all potential edge cases (empty inputs, single elements, boundary values, type variations, invalid inputs).
4. Algorithmic Pattern: What core algorithmic approach is likely needed (iterative, recursive, lookup table, built-in function, etc.)?
5. Critical Requirements: What must the solution absolutely handle to be correct (e.g., preserve order, handle duplicates, specific return type)?

Be thorough and precise. This analysis will guide all subsequent solution attempts.""",
            context=""
        )

        # Step 2: Parallel solution generation - explore multiple paradigms
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python solution using an IMPERATIVE approach (explicit loops, conditionals, state management).
Problem Analysis: {problem_analysis}
Guidelines:
- Handle all edge cases identified above
- Include explicit type handling and validation
- Prioritize clarity and robustness over brevity
- Return exactly the required data type
- Add inline comments for complex logic""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution using a FUNCTIONAL approach (map/filter/reduce, comprehensions, built-ins).
Problem Analysis: {problem_analysis}
Guidelines:
- Leverage Python's built-in functions and idioms
- Handle edge cases through conditional expressions or guards
- Ensure type consistency
- Prefer immutable operations where possible
- Document any non-obvious transformations""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python solution using a DECLARATIVE or MATH-BASED approach (formulas, lookups, mathematical transformations).
Problem Analysis: {problem_analysis}
Guidelines:
- Express the solution as directly as possible
- Use mathematical operations or lookup tables if applicable
- Handle edge cases with minimal conditional logic
- Ensure numerical precision and type correctness
- Comment on any domain-specific knowledge used""",
                context=problem_analysis
            )
        )

        # Step 3: Ensemble evaluation - select or synthesize the best solution
        selected_solution = await self.ensemble(
            instruction=f"""Evaluate these solution candidates and select the most robust implementation:

Evaluation Criteria:
1. Correctness: Does it handle all edge cases from the analysis?
2. Type Safety: Does it maintain proper input/output types?
3. Readability: Is the logic clear and well-commented?
4. Efficiency: Is it reasonably efficient for the problem scale?
5. Robustness: Does it fail gracefully on invalid inputs?

If one solution clearly dominates, select it. If they have complementary strengths, synthesize a hybrid solution that combines their best elements. Return only the final code with no additional text.""",
            contexts_list=solution_attempts
        )

        # Step 4: Iterative refinement - up to 2 revision cycles
        current_solution = selected_solution
        for iteration in range(2):
            revision = await self.revise(
                instruction=f"""Critically review this code and improve it:

Problem Analysis: {problem_analysis}

Revision Requirements:
1. Fix any off-by-one errors, boundary condition oversights, or type coercion issues
2. Add explicit handling for all edge cases mentioned in the analysis
3. Ensure return type exactly matches requirements (list vs tuple vs set)
4. Make error handling more defensive (e.g., validate inputs, handle unexpected types)
5. Improve code clarity with better variable names and comments
6. Remove any assumptions about input validity

If the code is already robust and handles all cases, return it unchanged. Otherwise, provide the improved version.""",
                context=current_solution
            )
            
            # Check if revision actually made changes (simple change detection)
            if revision.strip() == current_solution.strip():
                break
            current_solution = revision

        # Step 5: Final verification and simplification if needed
        # Check if solution still seems fragile (contains telltale phrases of uncertainty)
        if any(phrase in current_solution.lower() for phrase in ["assume", "should work", "probably", "might fail"]):
            # Fallback: Simplify and focus on correctness
            simplified_analysis = await self.summarize(
                instruction="Extract only the absolute core requirement and edge cases. Ignore elegance, focus purely on correctness.",
                context=problem_analysis
            )
            
            current_solution = await self.generate(
                instruction=f"""Generate the simplest possible correct solution based on this core requirement:

{simplified_analysis}

Requirements:
1. Handle only what is absolutely necessary for correctness
2. Explicitly check and handle every edge case
3. Use straightforward, defensive programming
4. Return exactly the required type
5. No clever optimizations - prioritize reliability

Return only the code.""",
                context=simplified_analysis
            )

        return current_solution