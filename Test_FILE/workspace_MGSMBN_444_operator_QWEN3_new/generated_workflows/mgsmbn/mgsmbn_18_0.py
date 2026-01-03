# Workflow ID: mgsmbn_18_0
# Benchmark: mgsmbn
# Data Indices: [94, 16]

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

        # === PHASE 1: PARALLEL PROBLEM DECOMPOSITION ===
        decomposition_tasks = [
            self.generate(
                instruction="""You are a mathematical linguist analyzing Bengali word problems.
                Extract ONLY the following from the problem:
                1. All numerical values with their associated entities (e.g., "5টি গাড়ি" → entity: গাড়ি, value: 5)
                2. All relationships between entities (ratios, sequences, comparisons)
                3. The explicit question being asked
                4. Any constraints (non-negative, integer-only, unit consistency)
                Format as JSON-like structure with keys: entities, relationships, question, constraints""",
                context=""
            ),
            self.generate(
                instruction="""You are a sequential logic analyzer.
                Reconstruct the problem as a timeline or step-by-step narrative:
                1. What happens first, second, third?
                2. What changes at each step?
                3. What accumulates or depletes?
                4. What is the final state we need to reach?
                Output as numbered steps with quantities and transitions.""",
                context=""
            ),
            self.generate(
                instruction="""You are a unit and constraint validator.
                Identify:
                1. All measurement units (টাকা, লিটার, ঘণ্টা, জিনিস, etc.)
                2. Implicit real-world constraints (no negative people, containers must be whole, etc.)
                3. Unit conversion needs (if any)
                4. Boundary conditions (minimum/maximum values)
                Format as bullet points with clear labels.""",
                context=""
            )
        ]
        
        decompositions = await asyncio.gather(*decomposition_tasks)
        
        # === PHASE 2: SYNTHESIZE UNIFIED PROBLEM MODEL ===
        unified_model = await self.ensemble(
            instruction="""You are a master problem synthesizer.
            You have three perspectives on the same Bengali math problem:
            1. Entity-relationship extraction
            2. Sequential/timeline analysis
            3. Unit and constraint mapping
            
            Your task:
            - Resolve any contradictions between perspectives
            - Merge into a single, coherent problem model
            - Preserve all numerical values, units, and constraints
            - Explicitly state what needs to be calculated
            - Flag any ambiguities or missing information
            Output format:
            PROBLEM MODEL:
            Entities: [list with values and units]
            Sequence: [step-by-step changes]
            Constraints: [list of hard constraints]
            Target: [what to solve for]""",
            contexts_list=decompositions
        )

        # === PHASE 3: VALIDATE & REFINE MODEL ===
        validated_model = await self.revise(
            instruction="""You are a ruthless validator.
            Critique the problem model:
            1. Are all units consistent? If not, suggest conversions.
            2. Do constraints make physical/logical sense? (e.g., no fractional people)
            3. Is the target clearly defined?
            4. Are there hidden steps or assumptions?
            5. Could any values be misinterpreted?
            Revise the model to fix all issues. If uncertain, add conservative assumptions.
            Output the corrected, bulletproof problem model.""",
            context=unified_model
        )

        # === PHASE 4: GENERATE MULTIPLE SOLUTION PATHS IN PARALLEL ===
        solution_tasks = [
            self.generate(
                instruction=f"""You are an algebraic solver.
                Given this problem model:
                {validated_model}
                
                Solve using algebraic equations:
                1. Define variables for unknowns
                2. Write equations based on relationships
                3. Solve step-by-step with full arithmetic
                4. Verify against constraints
                Show all work. Box final answer.""",
                context=validated_model
            ),
            self.generate(
                instruction=f"""You are a proportional reasoning expert.
                Given this problem model:
                {validated_model}
                
                Solve using ratios, fractions, or scaling:
                1. Identify base quantities and proportions
                2. Scale up/down as needed
                3. Handle remainders or distributions
                4. Cross-validate with constraints
                Show proportional logic clearly. Box final answer.""",
                context=validated_model
            ),
            self.generate(
                instruction=f"""You are a sequential calculator.
                Given this problem model:
                {validated_model}
                
                Solve by simulating each step chronologically:
                1. Start with initial state
                2. Apply each operation in sequence
                3. Track running totals
                4. Stop when target is reached
                Show state after each step. Box final answer.""",
                context=validated_model
            )
        ]
        
        raw_solutions = await asyncio.gather(*solution_tasks)

        # === PHASE 5: ENSEMBLE & VALIDATE SOLUTIONS ===
        final_answer = await self.ensemble(
            instruction="""You are the final arbiter.
            You have three solution attempts for the same problem:
            1. Algebraic approach
            2. Proportional approach
            3. Sequential simulation
            
            Your task:
            - Compare numerical answers
            - Check which solution best respects all constraints
            - Verify arithmetic correctness
            - Prefer solutions that handle edge cases (remainders, units, etc.)
            - If all agree, return the consensus answer
            - If conflict, pick the most physically plausible
            OUTPUT ONLY THE NUMERICAL ANSWER. No units. No explanation. Just the number.""",
            contexts_list=raw_solutions
        )

        # === PHASE 6: EXTRACTION & SANITY CHECK ===
        # Extract just the number (in case ensemble output has extra text)
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            clean_answer = match.group(0)
            # Final sanity revision: ensure it's not negative or absurd
            sanity_checked = await self.revise(
                instruction=f"""Given the answer: {clean_answer}
                Verify:
                1. Is it non-negative? (unless problem allows negatives)
                2. Is it integer if problem implies whole units? (containers, people, etc.)
                3. Does it match magnitude expectations? (not 1000x too big/small)
                If fails, return 0. Otherwise, return the same number.
                OUTPUT ONLY THE NUMBER.""",
                context=clean_answer
            )
            return sanity_checked.strip()
        else:
            return "0"  # Fallback