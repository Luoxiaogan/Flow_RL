# Workflow ID: mgsmbn_72_0
# Benchmark: mgsmbn
# Data Indices: [150, 72]

import asyncio

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

        # PHASE 1: STRUCTURED DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this Bengali math problem into atomic, interdependent subproblems. For each:
            1. Assign a unique ID (e.g., SP1, SP2)
            2. Describe what needs to be calculated or identified
            3. List prerequisite subproblem IDs (comma-separated, or "none" if independent)
            4. Specify expected data type (integer, float, boolean) and unit if applicable
            5. Note any constraints (e.g., "must be positive", "divisible by 3")
            
            Focus on causal and mathematical dependencies. Example: 
            "SP1: Total hay consumed by hamsters → depends on: none → type: integer → constraint: >0"
            "SP2: Hay per rat → depends on: SP1 → type: integer → constraint: divisible by cage count"
            
            Output as list of dictionaries with keys: id, description, dependencies, type, constraints.""",
            context=""
        )

        # PHASE 2: PARALLEL PERSPECTIVE EXTRACTION
        entity_extraction, math_modeling, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract all entities, quantities, and units from the problem. Structure as:
                - ENTITIES: [list with roles, e.g., "rats (subject)", "cages (container)"]
                - QUANTITIES: [list with values and descriptions, e.g., "3 cages", "6 hay per rat"]
                - UNITS: [list with unit types and contexts, e.g., "hay pieces (counting unit)"]
                - RELATIONSHIPS: [list mapping quantities to entities, e.g., "each rat → 6 hay pieces"]
                
                Be exhaustive. Include implicit entities (e.g., 'total hay' if not stated but calculable).""",
                context=""
            ),
            self.generate(
                instruction="""Model mathematical relationships as equations or pseudocode. For each relationship:
                1. Identify variables (use descriptive names like rats_per_cage)
                2. Write formula connecting them (e.g., total_hamster_hay = hamster_cages * hamsters_per_cage * hay_per_hamster)
                3. Mark knowns vs unknowns
                4. Note operation sequence (e.g., "subtract rabbit hay before dividing by rat cages")
                
                Prioritize dependency order matching decomposition phase. Use symbolic notation where helpful.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all explicit and implicit constraints. Categorize as:
                - DOMAIN CONSTRAINTS: Physical/logical limits (e.g., "no fractional rodents", "time > 0")
                - CALCULATION CONSTRAINTS: Mathematical requirements (e.g., "result must be integer", "divisible by 5")
                - CONTEXTUAL CONSTRAINTS: Real-world plausibility (e.g., "can't have negative money")
                
                For each, specify which subproblem(s) it affects and severity (critical vs warning).""",
                context=""
            )
        )

        # PHASE 3: ADVERSARIAL CODE GENERATION
        code_variants = await asyncio.gather(
            self.programmer(
                instruction=f"""Generate Python code solving the problem with INTEGER-ONLY assumptions.
                Context from decomposition: {json.dumps(decomposition[:3]) if len(decomposition) > 3 else json.dumps(decomposition)}
                Context from math modeling: {math_modeling[:500]}
                
                Rules:
                - Use integer division (//) where appropriate
                - Round only if explicitly justified
                - Validate against constraints: {constraint_analysis[:300]}
                - Print ONLY the final numerical answer (no explanations)
                - Handle edge cases (division by zero, negative results) with assertions""",
                context=f"Entities: {entity_extraction[:200]}\n\nMath Model: {math_modeling[:200]}"
            ),
            self.programmer(
                instruction=f"""Generate Python code solving the problem with FLOAT PRECISION.
                Context from decomposition: {json.dumps(decomposition[:3]) if len(decomposition) > 3 else json.dumps(decomposition)}
                Context from math modeling: {math_modeling[:500]}
                
                Rules:
                - Use float division (/) unless integer constraint exists
                - Round to 2 decimals only for final answer if needed
                - Validate against constraints: {constraint_analysis[:300]}
                - Print ONLY the final numerical answer
                - Include error handling for impossible scenarios""",
                context=f"Entities: {entity_extraction[:200]}\n\nMath Model: {math_modeling[:200]}"
            ),
            self.programmer(
                instruction=f"""Generate Python code using SYMBOLIC CONSTRAINT SOLVING (simulate sympy logic).
                Context from decomposition: {json.dumps(decomposition[:3]) if len(decomposition) > 3 else json.dumps(decomposition)}
                Context from math modeling: {math_modeling[:500]}
                
                Rules:
                - Represent unknowns as variables
                - Build equations from relationships
                - Solve symbolically where possible
                - Apply constraints as filters (e.g., [x for x in solutions if x > 0 and x.is_integer])
                - Print ONLY the final numerical answer
                - If multiple solutions, pick most contextually plausible""",
                context=f"Entities: {entity_extraction[:200]}\n\nMath Model: {math_modeling[:200]}"
            )
        )

        # PHASE 4: CONSTRAINT-AWARE ENSEMBLE
        final_answer = await self.ensemble(
            instruction=f"""Select the best answer from the three code variants below. Evaluate using:
            1. MATHEMATICAL CORRECTNESS: Does the code logically follow from problem?
            2. CONSTRAINT SATISFACTION: Does output meet all domain/calculation constraints from: {constraint_analysis[:400]}?
            3. UNIT/CONTEXT ALIGNMENT: Does answer make sense (e.g., integer rodents, positive time)?
            4. ROBUSTNESS: Does code handle edge cases gracefully?
            
            If multiple valid, prefer integer over float, simple over complex. If none valid, return "REVISION_NEEDED".
            Output ONLY the numerical answer or "REVISION_NEEDED" — no explanations.""",
            contexts_list=code_variants
        )

        # PHASE 5: ADAPTIVE REVISION (if needed)
        if "REVISION_NEEDED" in final_answer:
            diagnostic = await self.generate(
                instruction=f"""Diagnose why solutions failed. Analyze:
                - ENTITY ERRORS: Mismatched counts or misidentified relationships from: {entity_extraction[:300]}
                - MATH ERRORS: Incorrect formulas or sequence from: {math_modeling[:300]}
                - CONSTRAINT VIOLATIONS: Which constraints were broken per variant: {constraint_analysis[:300]}
                
                Output top 3 most probable failure causes ranked by likelihood.""",
                context=f"Previous answer: {final_answer}\n\nCode variants: {[c[:100] for c in code_variants]}"
            )

            # Revise the weakest link (entity extraction as most common failure point)
            revised_entities = await self.revise(
                instruction=f"""Improve entity extraction based on diagnostic: {diagnostic[:500]}
                Focus on:
                - Correcting miscounted entities (e.g., cage numbers, animal counts)
                - Clarifying ambiguous relationships (e.g., "per cage" vs "total")
                - Adding missed implicit quantities (e.g., totals, remainders)
                
                Output revised entity/quantity list in same format as original.""",
                context=entity_extraction
            )

            # Regenerate code with revised context
            fallback_code = await self.programmer(
                instruction=f"""Generate final code using REVISED entities and original math model.
                Revised entities: {revised_entities[:400]}
                Original math model: {math_modeling[:400]}
                Constraints: {constraint_analysis[:300]}
                
                Use most conservative assumptions (integer division, strict constraints).
                Print ONLY numerical answer.""",
                context=f"Diagnostic: {diagnostic[:200]}"
            )
            final_answer = fallback_code

        # Extract numerical answer from any text (defense against verbose outputs)
        answer_cleaning = await self.generate(
            instruction="""Extract ONLY the numerical answer from the text below. 
            If multiple numbers, pick the one that matches problem's expected output type (usually integer).
            If no clear number, return "0" as fallback.
            Output format: JUST the number, nothing else.""",
            context=final_answer
        )

        return answer_cleaning.strip()