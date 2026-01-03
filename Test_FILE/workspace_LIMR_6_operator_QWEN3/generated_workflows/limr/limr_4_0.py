# Workflow ID: limr_4_0
# Benchmark: limr
# Data Indices: [12, 276]

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

        # PHASE 1: META-CLASSIFICATION & DECOMPOSITION
        classification = await self.generate(
            instruction="""You are a world-class mathematical problem classifier. Analyze the problem with extreme care:

1. Primary Domain: Is this primarily algebraic, geometric, combinatorial, number-theoretic, or analytic?
2. Key Entities: List all variables, constants, functions, and constraints.
3. Hidden Structures: Are there symmetries, invariants, or transformations that simplify the problem?
4. Pitfalls: What are the most likely mistakes or misleading paths?
5. Solution Format: What form should the final answer take? (e.g., integer, interval, expression)

Output in structured JSON format with keys: "domain", "entities", "structures", "pitfalls", "format".""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems. For each:

- What must be computed or proven?
- What prerequisites are needed (reference other subproblem IDs)?
- What mathematical tools are most appropriate?

Prioritize subproblems that unlock others. Maximum 7 subproblems.""",
            context=classification
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Adopt a computational mathematician's mindset. Focus on algorithmic steps, variable substitutions, and exact calculations. Target eventual use of the programmer operator. Show all intermediate expressions.""",
            """Adopt a proof theorist's mindset. Seek elegant transformations, inequalities, or identities. Avoid brute force. Aim for a concise, insightful derivation.""",
            """Adopt a geometric visualizer's mindset. Even if not geometric, can you embed this in a coordinate system, vector space, or diagram? Use spatial intuition to guide algebra.""",
            """Adopt a combinatorial counter's mindset. Can this be reframed as counting, probability, or discrete structures? Look for bijections, recursions, or generating functions.""",
            """Adopt a wildcard innovator's mindset. Ignore conventional approaches. What non-obvious substitution, physical analogy, or 'outside the box' perspective could crack this open?"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

Work step by step. If you hit a dead end, note it and pivot. Output should include:
- Strategy summary
- Key steps
- Current progress (even if incomplete)
- Confidence estimate (0-100%)""",
                context=classification
            ) for instr in strategy_instructions]
        )

        # PHASE 3: ADVERSARIAL VALIDATION & CONFIDENCE SCORING
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""You are a skeptical peer reviewer. Assume this solution attempt is flawed.

1. Find the weakest logical link or most dubious assumption.
2. Check for algebraic errors, domain violations, or overlooked cases.
3. Assign a confidence score (0-100) based on rigor and completeness.
4. Suggest one concrete improvement.

Be brutally honest.""",
                context=attempt
            ) for attempt in strategy_attempts]
        )

        # Extract confidence scores for adaptive routing
        confidence_analysis = await self.generate(
            instruction="""Parse the following critique outputs to extract confidence scores and major concerns.
Output as JSON: {"scores": [list of scores], "major_concerns": [list of top concerns per strategy]}""",
            context="\n\n".join(critiques)
        )

        # PHASE 4: ADAPTIVE DEPTH & STRATEGY SELECTION
        confidence_data = json.loads(confidence_analysis)
        scores = confidence_data["scores"]

        # Select top 2 strategies for deepening
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:2]
        top_strategies = [strategy_attempts[i] for i in top_indices]
        top_critiques = [critiques[i] for i in top_indices]

        # Deepen top strategies with cross-pollination
        refined_strategies = []
        for i, (strat, crit) in enumerate(zip(top_strategies, top_critiques)):
            refined = await self.revise(
                instruction=f"""Improve this strategy using insights from critiques and other approaches:

Critique to address: {crit}

Cross-pollination: Incorporate useful elements from other strategies (especially Strategy {top_indices[1-i]+1} if applicable).

Expand to full solution. Show all steps. Verify each transformation.

If numerical answer is derivable, state it explicitly in required format.""",
                context=strat
            )
            refined_strategies.append(refined)

        # PHASE 5: SYNTHESIS, COMPUTATION & FINAL VERIFICATION
        # Use programmer for any computational verification
        computational_results = []
        for strat in refined_strategies:
            try:
                comp_result = await self.programmer(
                    instruction="""Extract any computable expressions or numerical claims from the solution. 
Implement and verify them with Python. Handle edge cases. Output should confirm or correct the proposed answer.""",
                    context=strat,
                    max_retries=2
                )
                computational_results.append(comp_result)
            except Exception:
                computational_results.append("COMPUTATION_FAILED")

        # Final ensemble synthesis
        final_answer = await self.ensemble(
            instruction="""You are the final arbiter. Given multiple solution attempts and computational verifications:

1. If all agree numerically, synthesize the most elegant proof.
2. If they conflict, identify the most rigorous and correct solution.
3. Ensure answer matches required format (e.g., integer 000-999, interval notation).
4. Output ONLY the final answer in the exact required format. No explanations.

Be decisive and precise.""",
            contexts_list=refined_strategies + computational_results
        )

        return final_answer