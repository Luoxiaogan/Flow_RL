# Workflow ID: mgsmbn_34_0
# Benchmark: mgsmbn
# Data Indices: [131, 71]

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

        # PHASE 1: SEMANTIC EXTRACTION & DECOMPOSITION
        # Extract key entities, quantities, and relationships from Bengali text
        relationship_extraction = await self.generate(
            instruction="""Perform deep semantic extraction of mathematical relationships from the Bengali problem. 
            Identify:
            1. All named entities (people, objects, places)
            2. All numerical values and their associated units (টাকা, বছর, টি, etc.)
            3. All comparative relationships (কম, বেশি, থেকে, এর চেয়ে, অর্ধেক, দ্বিগুণ)
            4. All operations implied (যোগ, বিয়োগ, গুণ, ভাগ)
            5. The final unknown to solve for
            
            Format output as structured key-value pairs using '=' notation. Example:
            Anakin_starfish = 10
            Laxin_starfish = Anakin_starfish - 5
            Total_fish = Anakin_starfish + Laxin_starfish + ...
            Jackson_age = ?
            
            Preserve Bengali units but translate operations to mathematical symbols.
            Flag any ambiguous phrases for later revision.""",
            context=""
        )

        # Break problem into dependent subproblems
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal computational subproblems. Each subproblem should:
            - Represent one atomic calculation or assignment
            - Have clearly defined inputs and outputs
            - Specify dependencies on other subproblems by ID
            - Include unit tracking for all quantities
            - Handle comparisons and relative quantities explicitly
            
            Prioritize dependency ordering: compute prerequisites before dependents.
            For age chains or sequential operations, enforce chronological/logical order.""",
            context=relationship_extraction
        )

        # PHASE 2: PARALLEL SOLUTION TRACKS
        # Track 1: Symbolic Code Execution
        code_solution = await self.programmer(
            instruction="""Generate Python code that computes the answer using ONLY the relationships provided.
            Requirements:
            - Define all variables explicitly
            - Perform calculations in dependency order
            - Include unit comments (even if not computable)
            - Handle integers and floats appropriately
            - Print ONLY the final numerical answer (no explanations)
            - If any calculation is impossible (negative people, fractional items), raise ValueError with reason
            
            Example structure:
            anakin_starfish = 10
            laxin_starfish = anakin_starfish - 5
            total = anakin_starfish + laxin_starfish + ...
            print(total)""",
            context=relationship_extraction,
            max_retries=2
        )

        # Track 2: Narrative Reasoning Chain
        narrative_solution = await self.generate(
            instruction=f"""Solve step-by-step as a thoughtful student would. Show your work:
            1. Restate the problem in your own words
            2. List known values and relationships
            3. Explain each calculation in sequence with reasoning
            4. Show intermediate results with units
            5. State final answer clearly
            
            Use Bengali units but English mathematical notation.
            If you encounter impossibility (negative fish, fractional children), explain why and adjust interpretation.
            Double-check that final answer makes real-world sense.
            
            Base your reasoning on these extracted relationships:
            {relationship_extraction}""",
            context=""
        )

        # PHASE 3: SYNTHESIS & VALIDATION
        # Merge and validate both solutions
        final_answer = await self.ensemble(
            instruction="""You have two solution approaches:
            1. CODE SOLUTION: Precise but brittle to parsing errors
            2. NARRATIVE SOLUTION: Robust but potentially imprecise
            
            Your task:
            - Compare numerical results. If they match, return that number.
            - If they differ, analyze which is more reliable:
              * Check code for unit mismatches or logic errors
              * Check narrative for arithmetic mistakes
              * Prefer narrative if code crashes on real-world constraints
            - If both are flawed, extract the most plausible answer from narrative reasoning
            - Final output must be ONLY a single number (integer or decimal) - nothing else""",
            contexts_list=[code_solution, narrative_solution]
        )

        # PHASE 4: CONTEXTUAL SANITY CHECK (Iterative Refinement)
        for refinement_round in range(2):
            sanity_check = await self.generate(
                instruction=f"""Validate this answer in real-world context:
                Answer: {final_answer}
                Problem: {self.problem_text[:200]}...
                
                Check:
                1. Is the number plausible? (No negative fish, no 200-year-old children)
                2. Do units make sense? (Can't add hours to kilometers)
                3. Does it satisfy all problem constraints?
                4. Is it consistent with extracted relationships?
                
                If valid, respond ONLY with "VALID".
                If invalid, respond with "INVALID: [concise reason]".""",
                context=final_answer
            )
            
            if "VALID" in sanity_check:
                break
            else:
                # Revise relationships and retry
                relationship_extraction = await self.revise(
                    instruction=f"""Previous answer failed sanity check: {sanity_check}
                    Re-extract relationships with conservative assumptions:
                    - Treat ambiguous comparatives as absolute differences unless context suggests otherwise
                    - Flag any fractional results for discrete entities (people, fish) as potential errors
                    - Explicitly state unit conversions if needed
                    - Recheck dependency ordering""",
                    context=relationship_extraction
                )
                
                # Quick recomputation with revised relationships
                code_solution = await self.programmer(
                    instruction="Recompute with revised relationships. Same format requirements.",
                    context=relationship_extraction,
                    max_retries=1
                )
                
                final_answer = await self.ensemble(
                    instruction="Select best answer from revised attempts. Return ONLY number.",
                    contexts_list=[code_solution, narrative_solution]
                )

        return final_answer