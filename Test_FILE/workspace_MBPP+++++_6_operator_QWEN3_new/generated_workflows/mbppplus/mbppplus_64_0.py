# Workflow ID: mbppplus_64_0
# Benchmark: mbppplus
# Data Indices: [246, 151]

import asyncio

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

        # STEP 1: CLASSIFY PROBLEM & ASSESS COMPLEXITY
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it using this framework:

1. Problem Type: 
   - Data Structure (list, tuple, set, dict operations)
   - Mathematical (number sequences, formulas, recurrence relations)
   - String Manipulation (parsing, formatting, pattern matching)
   - Algorithmic (searching, sorting, recursion, dynamic programming)
   - Logic/Validation (conditionals, comparisons, boolean logic)

2. Complexity Level:
   - Atomic (single operation, no decomposition needed e.g., list copy)
   - Composite (multiple distinct operations needed e.g., filter then sort)
   - Recursive/Dynamic (requires recurrence, memoization, or iterative buildup)

3. Edge Case Sensitivity:
   - Low (straightforward inputs, minimal edge cases)
   - High (must handle empty, single element, duplicates, negatives, type variations)

4. Solution Strategy Recommendation:
   - Direct Implementation (simple, one-pass solution)
   - Decomposition Required (break into subproblems)
   - Multiple Approaches Possible (generate alternatives and ensemble)

Output your analysis in JSON format with keys: "type", "complexity", "edge_sensitivity", "strategy_recommendation", "keywords" (list of important terms from problem).""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON CLASSIFICATION
        try:
            classification_data = json.loads(classification)
            strategy = classification_data.get("strategy_recommendation", "").lower()
            complexity = classification_data.get("complexity", "").lower()
        except:
            # Fallback: assume composite if classification fails
            strategy = "decomposition required"
            complexity = "composite"

        if "atomic" in complexity or "direct" in strategy:
            # Simple problems: go straight to solution generation
            solution = await self.programmer(
                instruction=f"""Implement a Python solution for this problem. 
                
Classification context: {classification}

Requirements:
- Handle all edge cases (empty inputs, single elements, duplicates, etc.)
- Match exact return type specified (list vs tuple vs set)
- Use the most straightforward and efficient approach
- Include no extra output or print statements
- Return only the function implementation as specified

Generate the code and test it internally against edge cases before returning.""",
                context=""
            )
            
            # Quick validation
            validation = await self.generate(
                instruction=f"""Review this solution for edge case handling and correctness:

{solution}

Check for:
1. Empty input handling
2. Single element cases
3. Type consistency
4. Return type matching
5. Algorithmic correctness

If any issues found, return 'REVISION_NEEDED' followed by specific issues. Otherwise, return 'VALID'.""",
                context=solution
            )
            
            if "REVISION_NEEDED" in validation:
                solution = await self.revise(
                    instruction=f"""Fix the following issues in the code:

{validation}

Ensure the solution is robust and handles all edge cases properly.""",
                    context=solution
                )
                
        else:
            # Complex problems: decompose and solve hierarchically
            decomposition = await self.decompose(
                instruction=f"""Decompose this programming problem into atomic subproblems based on its classification:

Classification: {classification}

For each subproblem, specify:
- What needs to be computed or transformed
- Any dependencies on other subproblems
- Expected input/output types
- Edge cases to consider

Ensure subproblems are granular enough to be solved independently but complete enough to compose into final solution.""",
                context=""
            )
            
            # Solve subproblems in parallel
            subproblem_solutions = []
            for subproblem in decomposition:
                sub_id = subproblem.get('id', 'unknown')
                sub_desc = subproblem.get('description', '')
                deps = subproblem.get('dependencies', '')
                
                # Generate solution for each subproblem
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem as part of a larger solution:

Subproblem ID: {sub_id}
Description: {sub_desc}
Dependencies: {deps}

Classification context: {classification}

Requirements:
- Focus only on this subproblem
- Handle edge cases specific to this subtask
- Return only the code implementation for this subtask
- Ensure output format matches what dependent subproblems expect""",
                    context=""
                )
                subproblem_solutions.append({
                    'id': sub_id,
                    'solution': sub_solution,
                    'description': sub_desc
                })
            
            # Compose final solution from subproblem solutions
            composition_context = "\n\n".join([
                f"Subproblem {sol['id']}: {sol['description']}\nSolution:\n{sol['solution']}"
                for sol in subproblem_solutions
            ])
            
            solution = await self.generate(
                instruction=f"""Compose a complete solution by integrating these subproblem solutions:

{composition_context}

Classification context: {classification}

Requirements:
- Create a cohesive function that solves the original problem
- Ensure proper data flow between subproblem solutions
- Handle edge cases at the integration level
- Return only the final function implementation as specified in the original problem
- Include no extra text or explanations""",
                context=composition_context
            )
            
            # Validate composed solution
            edge_cases = await self.generate(
                instruction=f"""Generate 5-7 comprehensive edge cases for this problem that are not mentioned in the basic examples:

Classification: {classification}

Include cases like:
- Empty inputs
- Single element inputs
- Maximum/minimum values
- Duplicate elements
- Type variations
- Boundary conditions

Format as Python assert statements.""",
                context=""
            )
            
            validation = await self.programmer(
                instruction=f"""Test the solution against these edge cases:

Solution:
{solution}

Edge Cases:
{edge_cases}

Run the tests and return 'PASSED' if all pass, or 'FAILED' with specific failing cases and errors.""",
                context=solution
            )
            
            if "FAILED" in validation:
                solution = await self.revise(
                    instruction=f"""Revise the solution to fix these failing edge cases:

{validation}

Ensure the revised solution passes all edge cases while maintaining core functionality.""",
                    context=solution
                )

        # FINAL OUTPUT EXTRACTION (ensure we return only the code)
        final_code = await self.generate(
            instruction="""Extract only the Python function implementation from the following text. 
            Remove any explanations, markdown formatting, or additional text. 
            Return ONLY the function code as it would appear in a Python file, including imports if any.
            Preserve exact function signature and return type.
            
            If no code is found, return an empty string.""",
            context=solution
        )
        
        return final_code.strip()