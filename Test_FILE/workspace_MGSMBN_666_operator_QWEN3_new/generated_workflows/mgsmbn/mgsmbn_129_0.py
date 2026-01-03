# Workflow ID: mgsmbn_129_0
# Benchmark: mgsmbn
# Data Indices: [153, 0]

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

        # PHASE 1: PROBLEM DECOMPOSITION & ENTITY EXTRACTION
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic computational subproblems.
        For each subproblem:
        - Clearly state what needs to be calculated
        - Identify required inputs (with units)
        - Specify output format and units
        - List dependencies (which other subproblems must be solved first)
        - Flag any ambiguities or missing information
        
        Structure each subproblem as:
        ID: [unique_id]
        Description: [what to compute]
        Inputs: [list with units]
        Output: [expected format]
        Dependencies: [comma-separated IDs or "none"]
        Ambiguities: [yes/no with explanation]
        
        Prioritize chronological or causal order. Group related quantities.
        """
        
        decomposition = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: PARALLEL EXTRACTION & INTERPRETATION
        extraction_instruction = """
        Extract all numerical values, units, and relationships from the original problem.
        Structure as JSON with keys:
        - entities: list of objects with {name, quantity, unit, role}
        - relationships: list of {subject, relation, object, formula_if_any}
        - constraints: list of boundary conditions or implicit rules
        - target: what final value must be computed
        
        Be meticulous. If a quantity is described indirectly (e.g., "twice as many"), 
        represent it as a relationship. Preserve Bengali units (টাকা, পাউন্ড, etc.).
        """
        
        interpretation_instruction = """
        Interpret the problem's narrative structure. Identify:
        - Temporal sequence (what happens first, next, last)
        - Causal relationships (what causes what)
        - Hidden assumptions (e.g., "all ducks eat equally")
        - Potential misinterpretations (common pitfalls)
        
        Format as structured analysis with clear headings.
        """

        # Run extraction and interpretation in parallel
        extraction_task = self.generate(
            instruction=extraction_instruction,
            context=""
        )
        interpretation_task = self.generate(
            instruction=interpretation_instruction,
            context=""
        )
        
        extraction_result, interpretation_result = await asyncio.gather(
            extraction_task, interpretation_task
        )

        # PHASE 3: VALIDATE & ENRICH DECOMPOSITION
        validation_instruction = f"""
        Given the problem decomposition and extracted entities/relationships:
        
        Decomposition: {json.dumps(decomposition, ensure_ascii=False, indent=2)}
        Entities/Relationships: {extraction_result}
        Narrative Analysis: {interpretation_result}
        
        Validate each subproblem:
        1. Are all required inputs available from extraction?
        2. Are dependencies correctly ordered?
        3. Do units match across dependencies?
        4. Are there any circular dependencies?
        5. Does narrative analysis suggest missing subproblems?
        
        For each subproblem, output:
        - Validation status (OK/ISSUE)
        - Missing inputs (if any)
        - Suggested fixes
        
        If major issues found, propose revised decomposition.
        """
        
        validation = await self.generate(
            instruction=validation_instruction,
            context=f"{extraction_result}\n\n{interpretation_result}"
        )

        # PHASE 4: CONDITIONAL SOLVING STRATEGY
        # Classify problem complexity to choose solving method
        classification_instruction = """
        Classify this problem based on:
        - Number of distinct operations required
        - Presence of fractions/decimals/percentages
        - Unit conversions needed
        - Multi-entity state tracking
        - Temporal dependencies
        
        Output classification as JSON with:
        {"complexity": "simple|moderate|complex", 
         "requires_code": true|false,
         "parallelizable_steps": [list of subproblem IDs that can be solved independently]}
        """
        
        classification = await self.generate(
            instruction=classification_instruction,
            context=validation
        )

        # Parse classification (in real implementation, use proper JSON parsing with error handling)
        requires_code = "true" in classification.lower() or "complex" in classification.lower()

        # PHASE 5: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem, extracted_data):
            sub_id = subproblem.get('id', 'unknown')
            desc = subproblem.get('description', '')
            deps = subproblem.get('dependencies', 'none')
            
            solve_instruction = f"""
            Solve subproblem {sub_id}: {desc}
            
            Context:
            - Extracted entities and relationships: {extracted_data}
            - Dependencies: {deps}
            - Validation feedback: {validation}
            
            Instructions:
            1. Show all calculation steps explicitly
            2. Track units at every step
            3. Verify intermediate results make sense
            4. If calculation involves division, fractions, or chained operations, use code
            5. Output final answer for this subproblem with units
            
            Format response as:
            Steps:
            [step-by-step reasoning]
            
            Answer: [numerical value with units]
            """
            
            # Use Programmer for complex math, Generate for simple arithmetic
            if requires_code and ("division" in desc.lower() or "fraction" in desc.lower() or "convert" in desc.lower()):
                result = await self.programmer(
                    instruction=solve_instruction,
                    context=extracted_data
                )
            else:
                result = await self.generate(
                    instruction=solve_instruction,
                    context=extracted_data
                )
            
            # Validate subproblem solution
            validation_instruction = f"""
            Validate this subproblem solution:
            Original subproblem: {desc}
            Solution: {result}
            Extracted data: {extracted_data}
            
            Check:
            - Units consistency
            - Numerical plausibility
            - Matches dependencies
            - No negative quantities where inappropriate
            - Decimal precision appropriate
            
            If issues found, suggest correction. Otherwise, output "VALID".
            """
            
            validation_result = await self.generate(
                instruction=validation_instruction,
                context=result
            )
            
            if "VALID" not in validation_result and "valid" not in validation_result:
                # Revise if validation fails
                result = await self.revise(
                    instruction=f"Fix issues identified: {validation_result}",
                    context=result
                )
            
            return {"id": sub_id, "solution": result, "validation": validation_result}

        # Solve subproblems in parallel where possible
        subproblem_tasks = [
            solve_subproblem(sp, extraction_result) 
            for sp in decomposition
        ]
        
        subproblem_results = await asyncio.gather(*subproblem_tasks)

        # PHASE 6: SYNTHESIZE FINAL ANSWER
        synthesis_instruction = f"""
        Synthesize final answer from subproblem solutions:
        {json.dumps(subproblem_results, ensure_ascii=False, indent=2)}
        
        Steps:
        1. Identify which subproblem contains the final target answer
        2. Verify all dependencies were correctly resolved
        3. Cross-check with original problem's question
        4. Ensure units match expected output
        5. Format as single numerical value (integer or decimal)
        
        If multiple candidates exist, use ensemble to select best.
        Output ONLY the numerical answer, nothing else.
        """
        
        # If multiple final candidates, use ensemble
        final_candidates = await asyncio.gather(
            self.generate(instruction=synthesis_instruction, context=json.dumps(subproblem_results)),
            self.generate(instruction="Alternative synthesis: trace calculation path from start to end", context=json.dumps(subproblem_results)),
            self.generate(instruction="Consistency check: does answer make sense in real-world context?", context=json.dumps(subproblem_results))
        )
        
        final_answer = await self.ensemble(
            instruction="Select the most accurate and consistent final numerical answer. Verify unit handling and calculation logic.",
            contexts_list=final_candidates
        )

        # PHASE 7: FINAL VALIDATION & OUTPUT
        verification_instruction = """
        Verify final answer against original problem:
        - Does it answer the exact question asked?
        - Is the magnitude reasonable? (e.g., not millions when expecting dozens)
        - Are units correct and consistent?
        - No fractional people/ducks unless specified
        - Matches all given constraints
        
        If verified, output answer as single number. If not, output "RETRY" to trigger workflow restart.
        """
        
        verified_answer = await self.revise(
            instruction=verification_instruction,
            context=final_answer
        )
        
        # Extract numerical answer (in real implementation, use regex or parsing)
        # For this template, we assume the answer is properly formatted
        return verified_answer.strip()