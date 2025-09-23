# Workflow ID: humaneval_67_0
# Benchmark: humaneval
# Data Indices: [138, 27]

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
        Universal workflow for generating precise Python functions from docstring specifications.
        Uses multi-perspective reasoning, adversarial critique, and ensemble synthesis.
        """
        import asyncio

        # PHASE 1: Problem Classification and Intent Extraction
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of the problem:

1. Extract the core task: What must the function compute or transform?
2. Classify the problem type: 
   - Mathematical (formulas, inequalities, number theory)
   - String/Text Transformation (case, format, encoding)
   - Algorithmic (loops, recursion, data structures)
   - Logical (boolean conditions, constraints)
3. Identify all example cases from the docstring. List them explicitly.
4. Infer implicit constraints: edge cases, type requirements, performance hints.
5. Determine the minimal sufficient condition for correctness.

Output a structured analysis with clear sections.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (Diamond Pattern)
        # Three diverse reasoning tracks
        math_track = asyncio.create_task(
            self.generate(
                instruction=f"""MATHEMATICAL/LOGICAL TRACK:
You are a mathematician deriving a closed-form solution.

Given problem analysis:
{problem_analysis}

Derive a mathematical or logical condition that must hold for the function to return the correct result.
- Show step-by-step reasoning
- Use inequalities, modular arithmetic, or algebraic identities if applicable
- Express the final condition as a single Python expression
- Consider edge cases: zero, negative numbers, empty inputs, etc.
- Your solution must be minimal and exact — no over-engineering

Output ONLY the final Python expression/function body, with no explanation.""",
                context=problem_analysis
            )
        )

        pattern_track = asyncio.create_task(
            self.generate(
                instruction=f"""PATTERN RECOGNITION TRACK:
You are a pattern recognition expert.

Given problem analysis:
{problem_analysis}

Analyze the example cases to identify computational patterns:
- What changes between inputs and outputs?
- What invariants or transformations are applied?
- Can you generalize from the examples to a rule?
- Express the rule as executable Python code

Output ONLY the final Python expression/function body, with no explanation.""",
                context=problem_analysis
            )
        )

        implementation_track = asyncio.create_task(
            self.generate(
                instruction=f"""IMPLEMENTATION-FIRST TRACK:
You are a pragmatic coder writing literal code.

Given problem analysis:
{problem_analysis}

Write Python code that directly implements the examples shown.
- Start by handling each example case explicitly
- Then generalize to a unified solution
- Prioritize clarity and correctness over cleverness
- Handle edge cases mentioned or implied

Output ONLY the final Python expression/function body, with no explanation.""",
                context=problem_analysis
            )
        )

        # Gather all three tracks
        math_solution, pattern_solution, implementation_solution = await asyncio.gather(
            math_track, pattern_track, implementation_track
        )

        # PHASE 3: Adversarial Self-Critique (Cascade with Feedback)
        # Each solution critiques itself
        math_critique = await self.revise(
            instruction="""Adversarial Self-Critique:
Assume your solution is WRONG. What edge cases, counterexamples, or logical flaws would break it?
- Test against all examples in the docstring
- Consider type mismatches, off-by-one errors, boundary conditions
- If you find a flaw, revise your solution to fix it
- If no flaw, explain why your solution is robust

Output the revised (or confirmed) solution ONLY.""",
            context=math_solution
        )

        pattern_critique = await self.revise(
            instruction="""Adversarial Self-Critique:
Assume your solution is WRONG. What edge cases, counterexamples, or logical flaws would break it?
- Test against all examples in the docstring
- Consider type mismatches, off-by-one errors, boundary conditions
- If you find a flaw, revise your solution to fix it
- If no flaw, explain why your solution is robust

Output the revised (or confirmed) solution ONLY.""",
            context=pattern_solution
        )

        implementation_critique = await self.revise(
            instruction="""Adversarial Self-Critique:
Assume your solution is WRONG. What edge cases, counterexamples, or logical flaws would break it?
- Test against all examples in the docstring
- Consider type mismatches, off-by-one errors, boundary conditions
- If you find a flaw, revise your solution to fix it
- If no flaw, explain why your solution is robust

Output the revised (or confirmed) solution ONLY.""",
            context=implementation_solution
        )

        # PHASE 4: Ensemble Synthesis with Cross-Validation
        final_solution = await self.ensemble(
            instruction=f"""SYNTHESIZE THE ULTIMATE SOLUTION:

You have three candidate solutions, each with self-critique:

1. Mathematical Solution:
{math_critique}

2. Pattern-Based Solution:
{pattern_critique}

3. Implementation-First Solution:
{implementation_critique}

Your task:
- Cross-validate each solution against ALL example cases in the original docstring
- Identify which solution is most robust, minimal, and correct
- If they agree, pick the simplest
- If they conflict, synthesize a new solution that combines their strengths and resolves their weaknesses
- Ensure the solution matches the ENTRY POINT function name and return type exactly
- NO over-engineering — implement exactly what's specified

Output ONLY the final Python function body (no def, no imports, just the code block).""",
            contexts_list=[math_critique, pattern_critique, implementation_critique]
        )

        return final_solution