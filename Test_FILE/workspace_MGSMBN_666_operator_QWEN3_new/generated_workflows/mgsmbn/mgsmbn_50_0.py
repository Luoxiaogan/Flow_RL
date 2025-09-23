# Workflow ID: mgsmbn_50_0
# Benchmark: mgsmbn
# Data Indices: [70]

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

        # PHASE 1: PARALLEL EXTRACTION & DECOMPOSITION
        # Spawn multiple perspectives to avoid single-point failure
        extraction_tasks = [
            self.generate(
                instruction="""Extract all mathematical entities, relationships, and constraints from the Bengali problem.
                Format as JSON with keys: 
                - "entities": list of {name, type, value_if_known}
                - "relationships": list of {subject, relation, object, mathematical_operator}
                - "unknowns": list of variables to solve for
                - "constraints": list of real-world or logical constraints (e.g., "must be integer", "non-negative")
                - "units": list of units mentioned and their context
                Be exhaustive. If value is unknown, mark as "unknown". Preserve Bengali terms but annotate with English equivalents.""",
                context=""
            ),
            self.decompose(
                instruction="""Break down the problem into minimal computational subproblems.
                Each subproblem should represent one atomic mathematical operation or logical step.
                Include dependencies if step B requires result of step A.
                Format each as: {"id": "step1", "description": "...", "dependencies": "step0,step2"}""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem type and required solution strategy.
                Choose from: sequential_operations, rate_problem, proportional_reasoning, distribution, comparison, multi_entity.
                Also identify: 
                - Primary mathematical operations needed
                - Potential pitfalls (e.g., unit conversion, hidden steps)
                - Expected answer format (integer/decimal)
                - Any implicit assumptions required
                Output in structured bullet points.""",
                context=""
            )
        ]

        # Execute in parallel
        entity_extraction, decomposition, problem_classification = await asyncio.gather(*extraction_tasks)

        # PHASE 2: SYNTHESIZE & VALIDATE DECOMPOSITION
        # Use ensemble to merge the best of structured decomposition and semantic extraction
        synthesis_contexts = [
            json.dumps({"type": "entity_extraction", "content": entity_extraction}),
            json.dumps({"type": "decomposition", "content": str(decomposition)}),
            json.dumps({"type": "classification", "content": problem_classification})
        ]

        refined_decomposition = await self.ensemble(
            instruction="""Synthesize the most reliable problem decomposition by combining:
            1. The structured subproblem breakdown
            2. The entity-relationship extraction
            3. The problem classification and strategy
            
            Output a unified JSON with:
            - "subproblems": list of {id, description, dependencies, required_entities, operation_type}
            - "validation_rules": list of checks to perform on final answer
            - "solution_strategy": step-by-step plan incorporating all perspectives
            - "constraints": consolidated list from all sources
            
            Prioritize decompositions that explicitly handle dependencies and units.""",
            contexts_list=synthesis_contexts
        )

        # PHASE 3: ADAPTIVE SOLUTION ROUTING
        # Check if problem requires symbolic solving or direct computation
        strategy_analysis = await self.generate(
            instruction=f"""Based on this refined decomposition:
            {refined_decomposition}
            
            Determine the optimal solution path:
            - If all subproblems are direct arithmetic with known values: "DIRECT_COMPUTATION"
            - If unknowns require equation setup: "SYMBOLIC_MODELING"
            - If iterative/constraint satisfaction needed: "CONSTRAINT_SATISFACTION"
            
            Also specify any unit conversion or precision requirements.
            Output in JSON format with "strategy" and "requirements" keys.""",
            context=refined_decomposition
        )

        # PHASE 4: EXECUTE STRATEGY
        if "DIRECT_COMPUTATION" in strategy_analysis or "SYMBOLIC_MODELING" in strategy_analysis:
            # Generate code that respects units and constraints
            solution_code = await self.generate(
                instruction=f"""Generate Python code to solve the problem based on:
                Decomposition: {refined_decomposition}
                Strategy: {strategy_analysis}
                
                Requirements:
                - Handle units appropriately (convert if needed, validate at end)
                - Enforce constraints (e.g., integer outputs for countable items)
                - Show intermediate steps as comments
                - Final answer must be assigned to variable 'final_answer'
                - No print statements except final_answer
                - Include validation checks from decomposition
                
                Example structure:
                # Step 1: Calculate X based on relationship Y
                x = ... 
                # Step 2: Apply constraint Z
                assert x >= 0, "Negative value not allowed"
                final_answer = x""",
                context=refined_decomposition
            )
            
            # Execute with retries
            computation_result = await self.programmer(
                instruction="Execute the generated code and return only the numerical result",
                context=solution_code,
                max_retries=3
            )
            
            raw_answer = computation_result
            
        else:
            # Fallback: multi-attempt ensemble
            solution_attempts = await asyncio.gather(
                self.programmer(
                    instruction=f"""Solve using algebraic approach. Define variables for unknowns.
                    Show equation setup and solving steps. Return only final number.""",
                    context=refined_decomposition
                ),
                self.programmer(
                    instruction=f"""Solve using step-by-step arithmetic. Calculate each subproblem in order.
                    Track units and validate intermediate results. Return only final number.""",
                    context=refined_decomposition
                )
            )
            
            raw_answer = await self.ensemble(
                instruction="""Select the most mathematically sound answer.
                Verify against problem constraints and decomposition.
                If both are valid but different, average them only if problem allows decimal answers.
                Otherwise, choose the integer solution.
                Return ONLY the numerical value.""",
                contexts_list=solution_attempts
            )

        # PHASE 5: VALIDATION & REFINEMENT LOOP
        for attempt in range(3):  # Max 3 refinement attempts
            validation = await self.generate(
                instruction=f"""Validate this answer against original problem:
                Answer: {raw_answer}
                Decomposition: {refined_decomposition}
                
                Check:
                1. Does it satisfy all extracted relationships?
                2. Does it respect all constraints (units, integer requirement, non-negative)?
                3. Is it consistent with problem classification?
                4. Are there any calculation errors in the steps?
                
                If valid, output "VALID: [answer]".
                If invalid, output "INVALID: [specific reason]" and suggest correction.""",
                context=raw_answer
            )
            
            if "VALID" in validation:
                break
            else:
                # Refine and recompute
                refined_approach = await self.revise(
                    instruction=f"""Based on validation feedback:
                    {validation}
                    
                    Revise the solution approach. Fix identified errors.
                    Maintain the same output format (single numerical value).""",
                    context=raw_answer
                )
                raw_answer = refined_approach

        # PHASE 6: FINAL OUTPUT SANITIZATION
        # Ensure pure numerical output
        final_answer = await self.revise(
            instruction="""Extract ONLY the numerical value from the following text.
            Remove any units, explanations, or formatting.
            If multiple numbers, choose the one that answers the original question.
            If no number, return 0.
            Output must be a single integer or decimal number.""",
            context=raw_answer
        )

        return final_answer.strip()