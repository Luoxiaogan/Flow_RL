# Workflow ID: mgsmbn_63_0
# Benchmark: mgsmbn
# Data Indices: [34, 81]

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

        # PHASE 1: SEMANTIC DECOMPOSITION
        # Extract structured narrative: entities, quantities, relationships, constraints
        decomposition = await self.generate(
            instruction="""You are a mathematical dramaturge. Transform the Bengali word problem into a structured narrative with:
            1. ENTITIES: List all actors/objects (e.g., Meredith, John, articles, glasses)
            2. QUANTITIES: Extract all numbers with their semantic roles (e.g., "4 hours per article", "5 articles on Monday")
            3. RELATIONSHIPS: Describe multiplicative/additive relationships (e.g., "Tuesday = Monday × (1 + 2/5)", "Wednesday = Tuesday × 2")
            4. CONSTRAINTS: Note temporal, logical, or unit constraints (e.g., "only weekdays", "no fractional people")
            5. TARGET: Explicitly state what is being asked (e.g., "total hours over three days")
            Format as a numbered list with clear section headers. Be exhaustive and precise.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        # Generate 3 independent solutions using different reasoning lenses
        strategy_instructions = [
            """Solve CHRONOLOGICALLY: Simulate the problem step-by-step as events unfold in time.
            - Start from initial state
            - Apply each action in sequence
            - Track cumulative quantities
            - Show intermediate results after each step
            - Final answer must be a single number with unit stripped""",
            
            """Solve ALGEBRAICALLY: Define variables and equations.
            - Assign symbols to unknowns
            - Write equations based on relationships
            - Solve symbolically first, then numerically
            - Show substitution steps
            - Final answer must be a single number with unit stripped""",
            
            """Solve via UNIT TRACKING: Focus on dimensional analysis and accumulation.
            - Identify base units (hours, articles, glasses)
            - Track how quantities transform through operations
            - Validate unit consistency at each step
            - Final answer must be a single number with unit stripped"""
        ]

        strategy_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) for instr in strategy_instructions]
        )

        # PHASE 3: CROSS-VALIDATION & SYNTHESIS
        # Ensemble compares solutions and synthesizes final answer
        ensemble_result = await self.ensemble(
            instruction="""You are a mathematical arbiter. Compare the three solution attempts:
            1. If all three agree numerically, output the consensus answer.
            2. If two agree and one differs, output the majority answer with note: "MAJORITY: <answer>".
            3. If all three differ, output "CONFLICT" followed by the three answers.
            Strip all units and explanations. Output ONLY the final number or "CONFLICT".
            Validate plausibility: reject negative counts, fractional people, or impossible magnitudes.""",
            contexts_list=strategy_solutions
        )

        # PHASE 4: ITERATIVE REFINEMENT (if conflict detected)
        final_answer = ensemble_result.strip()
        iteration = 0
        max_iterations = 2

        while "CONFLICT" in final_answer and iteration < max_iterations:
            iteration += 1
            
            # Revise by resolving discrepancies
            conflict_resolution = await self.revise(
                instruction=f"""RESOLVE CONFLICT from previous attempts:
                Previous conflicting answers: {final_answer}
                Re-examine the original problem for ambiguous phrases (e.g., 'গুণ বেশি' vs 'বেশি').
                Recalculate critical steps with explicit operator precedence.
                Validate unit consistency and real-world plausibility.
                Output ONLY the corrected numerical answer with units stripped.""",
                context=decomposition
            )
            
            # Generate one final verification attempt
            verification = await self.generate(
                instruction="""VERIFY the revised answer:
                - Recompute from scratch using chronological approach
                - Cross-check with algebraic formulation
                - Validate against problem constraints
                Output ONLY the final numerical answer with units stripped.""",
                context=conflict_resolution
            )
            
            final_answer = verification.strip()

        # EXTRACT NUMERICAL ANSWER (robust parsing)
        # Handle cases where answer might be embedded in text
        match = re.search(r'([-+]?\d*\.?\d+)', final_answer)
        if match:
            return float(match.group(1)) if '.' in match.group(1) else int(float(match.group(1)))
        else:
            # Fallback: return 0 if no number found (shouldn't happen in valid workflow)
            return 0