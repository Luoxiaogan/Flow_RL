# Workflow ID: mbppplus_92_0
# Benchmark: mbppplus
# Data Indices: [300, 174, 263]

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
        
        # Phase 1: Comprehensive problem analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Identify exact input type(s) and output type from function signature and description
            2. Extract all explicit constraints and requirements mentioned
            3. Infer implicit constraints and edge cases (empty inputs, single elements, boundary conditions, type mismatches)
            4. Classify problem type: mathematical, logical, string manipulation, data structure, or hybrid
            5. Identify potential solution approaches and common pitfalls for this problem type
            6. Note any performance or efficiency requirements
            7. List expected edge cases that must be handled
            Present analysis in structured format with clear sections.""",
            context=""
        )

        # Phase 2: Parallel solution generation from multiple perspectives
        mathematical_approach, algorithmic_approach, functional_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}

                Generate a solution using mathematical/algebraic approach:
                - Look for mathematical patterns, formulas, or number theory concepts
                - Consider closed-form solutions or mathematical optimizations
                - Focus on correctness and efficiency
                - Handle edge cases identified in analysis
                - Return solution as complete Python function with exact signature""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}

                Generate a solution using algorithmic/iterative approach:
                - Use step-by-step procedures with loops and conditionals
                - Focus on clear, readable logic that handles all edge cases
                - Consider time and space complexity
                - Return solution as complete Python function with exact signature""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}

                Generate a solution using functional/declarative approach:
                - Use Python built-ins like filter, map, list comprehensions, lambda
                - Focus on concise, readable code that leverages Python's functional features
                - Handle edge cases elegantly
                - Return solution as complete Python function with exact signature""",
                context=problem_analysis
            )
        )

        # Phase 3: Synthesize best solution from multiple approaches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the optimal solution from these three approaches:
            1. Compare solutions for correctness - which handles all edge cases best?
            2. Evaluate efficiency - time and space complexity
            3. Assess readability and Pythonic style
            4. Check adherence to exact function signature and return type
            5. Don't just pick one - create a hybrid that combines the best elements
            6. If one solution is clearly superior in all dimensions, select it
            7. Ensure final solution is complete, runnable Python code with exact required signature
            8. Add comments only if they significantly improve clarity""",
            contexts_list=[mathematical_approach, algorithmic_approach, functional_approach]
        )

        # Phase 4: Iterative refinement through validation
        current_solution = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            revised_solution = await self.revise(
                instruction=f"""Critically examine and improve this solution:
                Based on initial analysis: {problem_analysis}
                
                Check for:
                1. Edge case handling (empty inputs, single elements, boundary conditions)
                2. Type correctness (returning expected type - list vs tuple vs set)
                3. Performance issues or unnecessary complexity
                4. Readability and adherence to Python best practices
                5. Exact function signature compliance
                6. Potential off-by-one errors or logical flaws
                
                If improvements are needed, revise the solution accordingly.
                If no improvements needed, return the solution unchanged.
                Return complete Python function with exact required signature.""",
                context=current_solution
            )
            
            # Only update if revision made meaningful changes
            if revised_solution.strip() != current_solution.strip():
                current_solution = revised_solution
            else:
                break  # No changes needed, exit early

        return current_solution