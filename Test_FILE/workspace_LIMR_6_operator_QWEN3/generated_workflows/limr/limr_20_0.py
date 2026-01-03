# Workflow ID: limr_20_0
# Benchmark: limr
# Data Indices: [306, 182]

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

        # PHASE 0: CANONICAL ANCHORING — Define the answer contract upfront
        canonical_template = await self.generate(
            instruction="""You are solving a LIMR-style mathematical problem. The final answer MUST be an integer between 000 and 999.
            Before solving, explicitly state:
            - What form the answer will take (e.g., 'sum of coefficients', 'count of valid configurations', 'simplified radical expression parameters')
            - What mathematical objects will be summed or extracted to get the final integer
            - Any constraints the answer must satisfy (e.g., divisibility, range, parity)
            Output in JSON-like structure for easy parsing later.""",
            context=""
        )

        # PHASE 1: STRATEGIC DECOMPOSITION — Fork into parallel interpretations
        decomposition = await self.decompose(
            instruction="""Decompose this problem into 3-5 distinct solution strategies based on mathematical domains.
            For each strategy:
            - Name the domain (e.g., "Geometric Interpretation", "Number Theoretic Reduction", "Combinatorial Counting")
            - Describe the high-level approach in 1-2 sentences
            - List any key theorems, formulas, or techniques to apply
            - Do NOT solve yet — only outline the strategy.
            Ensure strategies are as diverse as possible to cover different mathematical lenses.""",
            context=canonical_template
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION — Generate solution sketches
        strategy_tasks = []
        for i, subprob in enumerate(decomposition):
            strategy_id = subprob['id']
            strategy_desc = subprob['description']
            
            task = self.generate(
                instruction=f"""Develop a detailed solution sketch for Strategy {strategy_id}: {strategy_desc}
                Adhere strictly to the canonical answer template provided earlier.
                Include:
                - Step-by-step reasoning with mathematical justification
                - Explicit formulas, equations, or algorithms to be used
                - Identification of potential pitfalls or assumptions
                - Intermediate expressions that will lead to the final integer
                If you reach an impasse, note it clearly and suggest an alternative within this strategy.
                Format output with clear section headers for easy parsing.""",
                context=f"Canonical Template: {canonical_template}"
            )
            strategy_tasks.append(task)
        
        strategy_sketches = await asyncio.gather(*strategy_tasks)

        # PHASE 3: CRITIQUE & REFINEMENT — Revise each sketch with adversarial feedback
        critique_tasks = []
        for sketch in strategy_sketches:
            critique = self.revise(
                instruction="""You are a skeptical mathematician reviewing this solution sketch.
                Your goal: Find flaws, gaps, or overcomplications.
                Specifically check:
                - Are all steps logically justified?
                - Are there unjustified assumptions?
                - Does the path clearly lead to an integer 000-999?
                - Are expressions simplified as much as possible?
                - Are there computational shortcuts or symmetries missed?
                Propose concrete improvements or alternative steps. If the sketch is irredeemable, recommend abandoning this strategy.
                Output should be structured: [Critique] followed by [Revised Sketch].""",
                context=sketch
            )
            critique_tasks.append(critique)
        
        refined_sketches = await asyncio.gather(*critique_tasks)

        # PHASE 4: COMPUTATIONAL VERIFICATION — Use programmer to validate & canonicalize
        verification_tasks = []
        for sketch in refined_sketches:
            verification = self.programmer(
                instruction=f"""Given this mathematical solution sketch, write Python code to:
                - Symbolically or numerically verify key steps
                - Compute the final answer in the form specified by the canonical template
                - Ensure the output is an integer between 000 and 999
                - If symbolic manipulation is needed (e.g., simplify radicals, rationalize denominators), use sympy
                - If brute-force is feasible (answer space 0-999), consider bounded search as validation
                Return the code and the computed integer. If multiple candidates, return all with confidence scores.
                IMPORTANT: The code must be self-contained and safe.""",
                context=f"Canonical Template: {canonical_template}\n\nSolution Sketch: {sketch}",
                max_retries=2
            )
            verification_tasks.append(verification)
        
        verification_results = await asyncio.gather(*verification_tasks)

        # PHASE 5: SYNTHESIS & ENSEMBLE — Merge the best insights into final answer
        final_answer = await self.ensemble(
            instruction="""You are the lead mathematician synthesizing multiple solution attempts.
            Given multiple verified solution paths and their computed answers:
            - Compare results for consistency
            - If all agree, output the consensus integer
            - If conflicting, identify which solution has the most rigorous derivation and fewest assumptions
            - Use the canonical template to validate the answer format
            - If still uncertain, propose a hybrid approach combining strongest elements
            Output ONLY the final integer answer as a 3-digit string (e.g., "024", "123", "999").""",
            contexts_list=verification_results
        )

        # PHASE 6: FINAL CANONICALIZATION — Ensure output matches required format
        sanitized_answer = await self.summarize(
            instruction="""Extract ONLY the 3-digit integer answer from the text below.
            Remove any markdown, explanations, or units.
            If multiple numbers, pick the one that matches canonical template.
            If no clear answer, return "000" as fallback.
            Output must be exactly 3 digits (pad with leading zeros if needed).""",
            context=final_answer
        )

        return sanitized_answer.strip()