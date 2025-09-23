# Workflow ID: mbppplus_27_0
# Benchmark: mbppplus
# Data Indices: [365, 338, 228]

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
        from typing import List, Dict, Any

        # Stage 1: Problem Deconstruction - Extract core components and contradictions
        problem_analysis = await self.generate(
            instruction="""Perform forensic analysis of the programming problem:

1. Extract the explicit task: What is the function supposed to do?
2. Identify input/output types: What data structures are involved?
3. Analyze test cases: What patterns do they reveal? Where do they contradict the reference solution?
4. List hidden assumptions: What edge cases are implied but not stated?
5. Flag inconsistencies: Where do examples, references, or descriptions conflict?

Structure your response as:
TASK: [concise description]
INPUT_TYPE: [e.g., list of tuples, list of dicts]
OUTPUT_TYPE: [e.g., list, string, dict]
TEST_PATTERNS: [key observations from test cases]
CONTRADICTIONS: [any conflicts between tests and reference]
EDGE_CASES: [implied edge conditions]
""",
            context=""
        )

        # Stage 2: Generate Three Independent Solution Hypotheses in Parallel
        hypothesis_tasks = [
            self.generate(
                instruction=f"""Generate Solution Hypothesis #1: Reference-Driven Approach

Based STRICTLY on the reference solution provided in the problem, implement the function.
Ignore test case outputs if they contradict the reference.
Focus on replicating the reference's logic, structure, and assumptions.
Include handling for basic edge cases (empty input, single element).

Context from problem analysis:
{problem_analysis}

Return ONLY the function implementation as specified in the output requirements.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis #2: Test-Case-Driven Approach

Based STRICTLY on the test case outputs, reverse-engineer the true specification.
Ignore the reference solution if it contradicts the test cases.
Analyze input-output pairs to deduce the actual transformation logic.
Ensure type consistency and handle edge cases implied by test patterns.

Context from problem analysis:
{problem_analysis}

Return ONLY the function implementation as specified in the output requirements.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis #3: Best-Practice-Driven Approach

Based on standard programming best practices for this problem category:
- Handle all edge cases (empty, single element, duplicates, type mismatches)
- Ensure type consistency and clean code
- Use efficient, readable algorithms
- Don't rely on reference or test cases if they seem flawed

Context from problem analysis:
{problem_analysis}

Return ONLY the function implementation as specified in the output requirements.""",
                context=problem_analysis
            )
        ]
        
        hypothesis_results = await asyncio.gather(*hypothesis_tasks)
        
        # Stage 3: Critique Each Hypothesis for Weaknesses and Edge Case Handling
        critique_tasks = []
        for i, hypothesis in enumerate(hypothesis_results):
            critique = await self.revise(
                instruction=f"""Critique Solution Hypothesis #{i+1}:

1. Does it pass ALL provided test cases? If not, which ones fail and why?
2. What edge cases does it NOT handle? (empty input, single element, duplicates, type issues)
3. Are there logical flaws or assumptions that could break in real usage?
4. Is the return type correct and consistent?
5. How does it compare to the other hypotheses in robustness?

Be brutally honest. Your goal is to find weaknesses, not to be polite.
Structure your response as a numbered list of specific issues.""",
                context=hypothesis
            )
            critique_tasks.append(critique)
        
        # Stage 4: Ensemble Synthesis - Combine Best Elements with Edge Case Hardening
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the Final Solution:

You have three solution hypotheses and their critiques. Your task:

1. SELECT the most promising base solution (usually the one that best matches test cases while being logically sound).
2. PATCH its weaknesses using insights from other hypotheses and critiques.
3. HARDEN against edge cases: explicitly handle empty inputs, single elements, duplicates, type mismatches.
4. ENSURE type consistency: match exact return types shown in tests.
5. RETURN ONLY the function implementation as specified in output requirements.

Guiding principles:
- Test cases define correctness, even if reference is wrong.
- When in doubt, prioritize robustness over elegance.
- Handle ALL edge cases mentioned in critiques.
- Preserve order if tests imply it matters.
- Never assume inputs are valid - validate defensively.

Final output must be production-ready, passing not just shown tests but hundreds of hidden edge cases.""",
            contexts_list=[f"Hypothesis {i+1}:\n{hyp}\n\nCritique:\n{crit}" 
                          for i, (hyp, crit) in enumerate(zip(hypothesis_results, critique_tasks))]
        )

        # Stage 5: Optional Self-Validation and Polish (One iteration only)
        validation = await self.generate(
            instruction="""Validate the final solution:

1. Does it handle empty input? Show how.
2. Does it handle single element? Show how.
3. Does it handle duplicates? Show how.
4. Is return type exactly as required?
5. Are there any remaining logical flaws?

If ANY issues are found, return a revised version that fixes them.
If no issues, return the original solution unchanged.

Return ONLY the function implementation (revised or original).""",
            context=final_solution
        )

        return validation