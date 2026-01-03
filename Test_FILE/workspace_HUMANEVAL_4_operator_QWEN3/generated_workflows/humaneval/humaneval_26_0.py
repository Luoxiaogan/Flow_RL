# Workflow ID: humaneval_26_0
# Benchmark: humaneval
# Data Indices: [2, 125]

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

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: Problem Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Perform deep semantic analysis of the problem:

1. Identify the primary domain: Is this mathematical, string/text processing, list/array manipulation, or algorithmic?
2. Determine the computational archetype: 
   - Transformation (mapping input to output)
   - Decomposition (breaking into parts)
   - Conditional branching (if/else logic)
   - Pattern recognition (regex, sequences)
   - Reduction (aggregating to single value)
3. Extract critical constraints:
   - Return type (int, float, list, etc.)
   - Edge cases implied by examples
   - Forbidden operations (if any)
4. List 3 most promising solution strategies with justification.

Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation
        solution_strategies = [
            """Strategy: Direct Mathematical Translation
Focus: For problems involving numbers, arithmetic, or algebraic decomposition.
Approach: Express solution as minimal mathematical operation. Prioritize built-in operators (%, //, abs) over complex logic.
Constraints: Must preserve floating-point precision. Return type must match examples exactly.
Instruction: Derive the simplest mathematical expression that satisfies all examples. Avoid conditionals unless absolutely necessary.""",
            
            """Strategy: State-Based Parsing
Focus: For string/list problems with conditional delimiters or transformations.
Approach: Implement explicit if/elif/else chains based on presence of key characters (spaces, commas, etc.). Use built-in methods (split, replace, islower).
Constraints: Handle edge cases like empty strings, single characters, mixed case.
Instruction: Write imperative code that checks conditions in order of priority as implied by examples. Include fallback for 'else' case.""",
            
            """Strategy: Example-Driven Pattern Induction
Focus: When examples reveal a clear input-output pattern.
Approach: Generalize from provided examples. Look for positional patterns, character properties (odd/even ord), or structural invariants.
Constraints: Solution must extrapolate correctly beyond given examples.
Instruction: Infer the underlying rule from examples. Implement as either direct computation or minimal iteration. Prefer list comprehensions for filtering/mapping."""
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(
                instruction=f"""{strategy}

Problem Context:
{classification}

Generate ONLY the Python function body (no signature, no imports). 
Ensure return type matches examples precisely. 
Handle edge cases mentioned in classification.
Code must be minimal and directly executable.""",
                context=classification
            ) for strategy in solution_strategies
        ]
        
        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 3: Cross-Validation & Ensemble Synthesis
        validation_narratives = await asyncio.gather(*[
            self.generate(
                instruction=f"""Critically evaluate this solution:

1. Does it satisfy ALL examples in the docstring? Walk through each.
2. Does it handle edge cases identified in classification?
3. Is return type correct? (e.g., int vs float)
4. Any precision issues? (e.g., floating-point errors)
5. Is the code minimal and readable?

If flawed, explain exactly why and how to fix.

Solution to evaluate:
{s}""",
                context=classification
            ) for s in raw_solutions
        ])

        # Synthesize best solution
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the optimal solution:

Criteria:
1. Correctness: Must pass all docstring examples
2. Robustness: Handles edge cases from classification
3. Simplicity: Minimal, readable code
4. Precision: Correct return type and no floating-point drift

If one solution is clearly superior, select it. 
If multiple have complementary strengths, merge them.
If all are flawed, create a new solution incorporating fixes from validation narratives.

Output ONLY the Python function body (no explanations).""",
            contexts_list=[f"Solution: {s}\n\nValidation: {v}" 
                          for s, v in zip(raw_solutions, validation_narratives)]
        )

        # PHASE 4: Edge Case Refinement & Final Formatting
        edge_refined = await self.revise(
            instruction=f"""Enhance solution with explicit edge case handling:

Based on classification: {classification}

1. Add handling for boundary conditions (empty input, zero, single element, etc.)
2. Ensure type consistency (e.g., always return float even for 0.0)
3. Fix any precision issues (use abs(diff) < 1e-6 for float comparisons if needed)
4. Verify function name matches ENTRY POINT exactly

Output ONLY the complete Python function including signature. 
Example format:
def truncate_number(number: float) -> float:
    return number % 1.0""",
            context=final_solution
        )

        # Final cleanup: Ensure exact function signature
        signature_match = re.search(r'def\s+\w+\s*\(.*?\)\s*->\s*.*?:', self.problem_text)
        if signature_match:
            required_signature = signature_match.group(0)
            # Extract function name for verification
            func_name = re.search(r'def\s+(\w+)', required_signature).group(1)
            
            # Ensure output starts with correct signature
            if not edge_refined.strip().startswith(required_signature.split(':')[0]):
                # Reconstruct with correct signature
                body = edge_refined.split('\n', 1)[1] if '\n' in edge_refined else ''
                edge_refined = f"{required_signature}\n{body}"
            
            # Final verification that function name is preserved
            if func_name not in edge_refined.split('(')[0]:
                edge_refined = edge_refined.replace(
                    edge_refined.split('(')[0].split()[-1], 
                    func_name
                )

        return edge_refined.strip()