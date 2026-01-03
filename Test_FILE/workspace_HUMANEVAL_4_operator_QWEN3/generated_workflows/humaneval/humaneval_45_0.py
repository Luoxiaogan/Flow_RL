# Workflow ID: humaneval_45_0
# Benchmark: humaneval
# Data Indices: [144, 131]

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
        Universal code generation workflow for specification-driven function implementation.
        Uses parallel decomposition, hypothesis generation, validation, and refinement.
        """
        import asyncio
        import re

        # Stage 1: Parallel Problem Decomposition
        decomposition_tasks = [
            self.generate(
                instruction="""Extract all examples from the docstring. 
                For each example, parse it into:
                - Input arguments (as Python literals)
                - Expected output (as Python literal)
                - Line number or identifier if available
                Format as a JSON-like list of dictionaries: [{"input": [...], "output": ..., "id": "..."}, ...]
                Be meticulous — missing one example breaks the solution.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the examples to infer:
                - Return type (int, float, bool, str, list, etc.) — be precise
                - Edge cases (empty inputs, zeros, single elements, boundaries)
                - Implicit constraints (e.g., "positive whole numbers", "no zero denominator")
                - Any pattern or formula connecting inputs to outputs
                Summarize in structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem type and suggest solution strategies:
                - Category: String manipulation, Mathematical, List processing, Algorithmic, Other
                - Recommended Python constructs: (e.g., string.split, int(), % operator, loops, recursion)
                - Potential libraries (if any): (e.g., math, re, fractions) — but prefer built-ins
                - Warning: Do NOT over-engineer — implement exactly what examples demonstrate
                Output as categorized sections.""",
                context=""
            )
        ]
        example_analysis, type_analysis, strategy_analysis = await asyncio.gather(*decomposition_tasks)

        # Stage 2: Generate Multiple Solution Hypotheses
        hypothesis_instructions = [
            f"""Generate a solution that strictly mimics the examples.
            Use the following extracted examples:
            {example_analysis}
            
            Implement the minimal code that reproduces these outputs.
            Do NOT generalize beyond what is demonstrated.
            Prioritize literal interpretation over cleverness.""",
            
            f"""Generate a solution based on inferred mathematical/formulaic patterns.
            From the analysis:
            {type_analysis}
            
            Derive a general formula or algorithm.
            Use variables and expressions that match the inferred logic.
            Still ensure it passes all examples.""",
            
            f"""Generate a solution that prioritizes edge case handling.
            From edge case analysis:
            {type_analysis}
            
            Structure code to explicitly handle special cases first.
            Use conditionals if needed.
            Ensure main logic still covers standard cases."""
        ]

        hypothesis_candidates = []
        for instr in hypothesis_instructions:
            candidate = await self.generate(instruction=instr, context="")
            hypothesis_candidates.append(candidate)

        # Stage 3: Validate Each Hypothesis Against Examples
        validation_tasks = []
        for i, candidate in enumerate(hypothesis_candidates):
            validation = await self.revise(
                instruction=f"""Validate this candidate solution against ALL extracted examples:
                {example_analysis}
                
                For each example:
                - Mentally simulate execution
                - Check if output matches exactly (type and value)
                - Note any mismatches or ambiguities
                
                Summarize as:
                "Candidate {i+1}:
                - Passes: [list example IDs]
                - Fails: [list example IDs with reasons]
                - Confidence: High/Medium/Low"
                
                Be brutally honest — even one failure disqualifies it unless fixable.""",
                context=candidate
            )
            validation_tasks.append(validation)

        validation_results = await asyncio.gather(*validation_tasks)

        # Stage 4: Ensemble Selection — Pick Best or Synthesize
        selected_solution = await self.ensemble(
            instruction="""Select the best candidate solution based on:
            - Highest number of passing examples
            - Correct handling of edge cases
            - Simplicity and minimalism (no extra features)
            - Faithfulness to example behavior (not theoretical perfection)
            
            If two candidates are equally good, merge their strengths.
            If all fail, pick the one with the most fixable errors.
            
            Output ONLY the raw Python code — no explanations, no markdown.
            Ensure function name matches ENTRY POINT exactly.""",
            contexts_list=hypothesis_candidates  # Code candidates
        )

        # Stage 5: Final Refinement — Ensure Compliance
        final_code = await self.revise(
            instruction=f"""Refine this code to meet ALL requirements:
            - Function name must exactly match ENTRY POINT from original problem.
            - Return types must match examples precisely (int vs float matters).
            - Remove any imports unless absolutely necessary (add inside this method if needed).
            - No comments, no extra whitespace, no logging.
            - Handle all edge cases implied by examples.
            - Code must be minimal — delete any line not required by examples.
            
            If any doubt, prefer the behavior shown in examples over generalization.
            
            Output ONLY the final, clean, ready-to-run Python function code.""",
            context=selected_solution
        )

        return final_code