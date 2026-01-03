# Workflow ID: humaneval_10_0
# Benchmark: humaneval
# Data Indices: [7, 79]

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
        Universal workflow for generating Python functions from specifications.
        Uses parallel candidate generation, iterative refinement, and ensemble synthesis.
        """
        import asyncio
        import re

        # Phase 1: Structural Analysis - Extract key components from the problem
        structural_analysis = await self.generate(
            instruction="""Perform deep structural analysis of the code generation problem. Extract and organize:

1. FUNCTION SIGNATURE: Identify exact function name, parameters, and return type annotation (if any)
2. DOCSTRING CONTENT: Break down into:
   - Behavioral description (what the function should do)
   - Examples (extract as input-output pairs, preserve exact formatting)
   - Any explicit constraints or edge cases mentioned
3. ENTRY POINT: Confirm the exact function name that must be implemented
4. RETURN TYPE INFERENCE: Analyze examples to determine expected return type (int, float, list, string, etc.)
5. EDGE CASES: Identify any boundary conditions from examples (empty inputs, zero values, single elements, etc.)

Present your analysis in a structured JSON-like format with clear section headers. Be meticulous - every detail matters for correct implementation.""",
            context=""
        )

        # Phase 2: Parallel Candidate Generation - Three distinct strategies
        candidate_tasks = [
            # Strategy 1: Example-Driven Pattern Extraction
            self.generate(
                instruction=f"""Generate a Python function implementation using PURE EXAMPLE-DRIVEN REASONING.

Guidelines:
- Treat the examples in the docstring as the primary specification
- Extract patterns from input-output pairs
- Generalize the pattern to handle unseen inputs
- Preserve exact function name from ENTRY POINT
- Match return types exactly as shown in examples (int vs float matters)
- Handle edge cases observed in examples (empty lists, zero, etc.)
- Use simplest possible implementation that satisfies all examples
- Do NOT add extra features or over-engineer

Base your reasoning entirely on the structural analysis:
{structural_analysis}

Output ONLY the Python function code, nothing else.""",
                context=structural_analysis
            ),
            # Strategy 2: Specification-Driven Translation
            self.generate(
                instruction=f"""Generate a Python function implementation using SPECIFICATION-DRIVEN TRANSLATION.

Guidelines:
- Focus on the natural language description in the docstring
- Translate requirements into code literally
- Use standard library functions when appropriate
- Ensure function name matches ENTRY POINT exactly
- Return types must match examples precisely
- Consider edge cases mentioned in specification
- Code should be clean, readable, and efficient
- Handle all cases implied by the specification, not just examples

Base your reasoning on the structural analysis:
{structural_analysis}

Output ONLY the Python function code, nothing else.""",
                context=structural_analysis
            ),
            # Strategy 3: Edge-Case Optimized Implementation
            self.generate(
                instruction=f"""Generate a Python function implementation optimized for EDGE CASES and ROBUSTNESS.

Guidelines:
- Prioritize handling of edge cases identified in structural analysis
- Ensure function works correctly for boundary conditions
- Add explicit checks for special cases if needed
- Function name must match ENTRY POINT exactly
- Return types must be consistent with examples
- Code should be defensive but not over-engineered
- Consider performance implications for edge cases
- Verify that implementation satisfies all examples

Base your reasoning on the structural analysis:
{structural_analysis}

Output ONLY the Python function code, nothing else.""",
                context=structural_analysis
            )
        ]

        # Execute parallel generation
        candidates = await asyncio.gather(*candidate_tasks)

        # Phase 3: Revision - Refine each candidate for correctness and adherence
        revision_tasks = []
        for i, candidate in enumerate(candidates):
            revision_tasks.append(
                self.revise(
                    instruction=f"""Revise this candidate implementation for correctness and adherence to specification.

Critical checks:
1. FUNCTION NAME: Must match ENTRY POINT exactly
2. RETURN TYPE: Must match examples precisely (int vs float, list vs tuple, etc.)
3. EDGE CASES: Must handle all edge cases identified in structural analysis
4. EXAMPLES: Must satisfy all provided examples
5. CLEAN CODE: Remove any unnecessary complexity or over-engineering
6. NO EXTRA FEATURES: Implement exactly what's specified, nothing more

Structural analysis for reference:
{structural_analysis}

Candidate {i+1}:
{candidate}

Output ONLY the revised Python function code, nothing else.""",
                    context=candidate
                )
            )

        # Execute parallel revision
        revised_candidates = await asyncio.gather(*revision_tasks)

        # Phase 4: Ensemble Synthesis - Select or merge the best solution
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these revised candidates.

Evaluation criteria (in order of priority):
1. CORRECTNESS: Must handle all examples and edge cases correctly
2. SIMPLICITY: Prefer the most straightforward, readable implementation
3. ADHERENCE: Must match function name and return types exactly
4. ROBUSTNESS: Should handle edge cases gracefully
5. EFFICIENCY: Prefer more efficient solutions when correctness is equal

Structural analysis for reference:
{structural_analysis}

Candidates:
{chr(10).join([f'Candidate {i+1}:{chr(10)}{candidate}' for i, candidate in enumerate(revised_candidates)])}

Output ONLY the final Python function code, nothing else. This will be submitted as the solution.""",
            contexts_list=revised_candidates
        )

        return final_solution