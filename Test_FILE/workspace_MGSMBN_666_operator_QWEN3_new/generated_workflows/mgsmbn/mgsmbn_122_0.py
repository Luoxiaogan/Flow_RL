# Workflow ID: mgsmbn_122_0
# Benchmark: mgsmbn
# Data Indices: [113, 12]

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
        import re

        # STEP 1: CLASSIFY & EXTRACT STRUCTURED PROBLEM DNA
        classification = await self.generate(
            instruction="""Analyze this Bengali math problem with extreme precision. Output must be a structured plain-text block with exactly these sections:

[PROBLEM_TYPE]
Identify primary category: rate, distribution, comparison, sequential, proportional, or multi_entity. Choose one.

[COMPLEXITY]
simple (single operation) | multi_step (sequential dependencies) | decomposable (independent subproblems)

[HIDDEN_CONSTRAINTS]
List any implicit constraints: e.g., "no negative items", "must be integer", "time cannot exceed X"

[ENTITIES]
List all named entities (people, objects, places) and their roles.

[VALUES]
Extract all numbers with their semantic meaning. Format: "variable_name = value (unit) # context"

[RELATIONS]
Describe mathematical relationships: "A is twice B", "rate = questions/hour", etc.

[UNKNOWN]
State exactly what needs to be calculated.

[STRUCTURE]
If multi_step or decomposable, outline calculation sequence.

Be brutally concise. No explanations. Only structured data.""",
            context=""
        )

        # STEP 2: META-COGNITIVE BRANCHING DECISION
        strategy = await self.revise(
            instruction="""Based on the classification, output a single-line strategy directive in this exact format:
"DIRECTIVE: [simple_solve | decompose_parallel | ensemble_validate]"

Rules:
- If COMPLEXITY is 'simple' → simple_solve
- If COMPLEXITY is 'multi_step' → simple_solve (sequential handled in code)
- If COMPLEXITY is 'decomposable' → decompose_parallel
- If HIDDEN_CONSTRAINTS contains ambiguity or multiple interpretations → ensemble_validate
- Default: simple_solve""",
            context=classification
        )

        directive = strategy.strip().split("DIRECTIVE: ")[-1] if "DIRECTIVE: " in strategy else "simple_solve"

        # STEP 3: ADAPTIVE SOLVING PATH
        if directive == "decompose_parallel":
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction="""Break problem into independent subproblems. Each subproblem must be solvable with the extracted values. 
                Prioritize: 
                1. Temporal separation (Day 1 vs Day 2)
                2. Entity separation (Person A vs Person B)
                3. Conceptual separation (Distance vs Time)
                Output minimal necessary subproblems.""",
                context=classification
            )
            
            # Solve subproblems in parallel
            async def solve_subproblem(sp):
                return await self.programmer(
                    instruction=f"""Solve this subproblem using ONLY values from classification context.
                    Subproblem: {sp['description']}
                    Write Python code with clear variable names reflecting units.
                    Include assertions for intermediate sanity checks.
                    Output only final numerical result.""",
                    context=classification
                )
            
            sub_results = await asyncio.gather(*[solve_subproblem(sp) for sp in subproblems])
            
            # Synthesize results
            final_computation = await self.programmer(
                instruction="""Combine subproblem results into final answer. 
                Subproblem results: """ + "; ".join(sub_results) + """
                Write code that performs final aggregation (sum, difference, etc.).
                Include unit consistency checks.
                Output only the final number.""",
                context=classification
            )
            
        elif directive == "ensemble_validate":
            # Generate 3 solution perspectives in parallel
            perspectives = await asyncio.gather(
                self.programmer(
                    instruction="""Solve using literal interpretation of text. 
                    Extract values directly. No assumptions. 
                    Code must include explicit unit tracking.""",
                    context=classification
                ),
                self.programmer(
                    instruction="""Solve using algebraic modeling. 
                    Define variables for unknowns. Set up equations. 
                    Solve symbolically then numerically.""",
                    context=classification
                ),
                self.programmer(
                    instruction="""Solve using proportional reasoning. 
                    Identify ratios, scale factors, or percentage relationships.
                    Apply cross-multiplication or unit rate methods.""",
                    context=classification
                )
            )
            
            # Ensemble select best answer
            final_computation = await self.ensemble(
                instruction="""Select the most plausible answer. Criteria:
                1. Matches problem constraints (from classification)
                2. Mathematically consistent across methods
                3. Real-world plausible (no negative people, etc.)
                If all agree, return any. If conflict, pick the one satisfying most constraints.
                Output ONLY the numerical answer.""",
                contexts_list=perspectives
            )
            
        else:  # simple_solve or multi_step
            final_computation = await self.programmer(
                instruction="""Solve the problem end-to-end using extracted values and relations.
                Steps:
                1. Map values to variables with unit suffixes (e.g., questions_per_hour)
                2. Implement calculation sequence from [STRUCTURE]
                3. Include intermediate assertions (e.g., assert time > 0)
                4. Apply constraints from [HIDDEN_CONSTRAINTS]
                5. Output ONLY final numerical result.
                
                Example structure for rate problem:
                total_questions = rate * time
                unanswered = total_available - total_questions""",
                context=classification
            )

        # STEP 4: MANDATORY VALIDATION & REVISION
        validated = await self.revise(
            instruction=f"""SANITY CHECK: Given computed result "{final_computation}" and original problem, verify:
            - Is the number positive? (unless context allows negative)
            - Is it integer if problem implies whole items? 
            - Does it match scale? (e.g., not 1000 when inputs are ~10)
            - Does it satisfy all HIDDEN_CONSTRAINTS?
            
            If valid: output exactly "VALID: [number]"
            If invalid: output "INVALID: [correction]" with corrected calculation.
            
            Be ruthless. When in doubt, INVALID.""",
            context=f"Classification:\n{classification}\n\nComputation:\n{final_computation}"
        )

        # STEP 5: ERROR RECOVERY LOOP (one retry)
        if "INVALID:" in validated:
            correction = validated.split("INVALID: ")[-1]
            final_computation = await self.programmer(
                instruction=f"""Re-solve with this correction: {correction}
                Use same structured approach but fix the identified error.
                Output ONLY final numerical result.""",
                context=classification
            )

        # STEP 6: EXTRACT PURE NUMERICAL ANSWER
        # Clean any residual text, keep only number (integer or decimal)
        match = re.search(r'[-+]?\d*\.?\d+', str(final_computation))
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is (let grading handle)
            return str(final_computation).strip()