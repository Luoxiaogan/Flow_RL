# Workflow ID: mgsmbn_123_0
# Benchmark: mgsmbn
# Data Indices: [170]

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

        # STEP 1: Generate initial problem schema with deep semantic parsing
        schema = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math problem. Construct a structured mathematical schema including:
            1. KNOWN_QUANTITIES: List all numbers with their contextual meaning and units (e.g., "1.5 miles - width of park")
            2. UNKNOWN_QUANTITIES: What needs to be calculated? Specify expected unit.
            3. RELATIONSHIPS: Mathematical relationships between quantities (addition, multiplication, ratios, rates, etc.)
            4. CONSTRAINTS: Real-world constraints (non-negative, integer-only, unit consistency)
            5. TEMPORAL_SEQUENCE: If time-based, outline chronological order of events
            6. HIDDEN_STEPS: Any implied calculations not explicitly stated
            Format as JSON with these exact keys. Be exhaustive and precise.""",
            context=""
        )

        # STEP 2: Validate and refine schema
        refined_schema = await self.revise(
            instruction="""Critically review the mathematical schema. Check for:
            - Missing quantities or relationships
            - Unit inconsistencies (e.g., mixing hours and minutes)
            - Logical gaps in reasoning chain
            - Violations of real-world constraints
            - Ambiguous phrasing that needs clarification
            Improve completeness and precision. Maintain JSON format.""",
            context=schema
        )

        # STEP 3: Classify problem complexity
        complexity = await self.generate(
            instruction=f"""Based on this refined schema:
            {refined_schema}
            
            Classify problem complexity:
            - SIMPLE: Single operation, no hidden steps, single entity
            - MODERATE: Multiple operations but linear sequence
            - COMPLEX: Multiple entities, conditional logic, or hierarchical dependencies
            Also identify primary mathematical archetype: RATE, PROPORTION, SEQUENTIAL, DISTRIBUTION, COMPARISON, MULTI_ENTITY
            Return as JSON: {{"complexity": "...", "archetype": "..."}}""",
            context=refined_schema
        )

        # STEP 4: Conditional branching based on complexity
        try:
            complexity_data = json.loads(complexity)
            problem_complexity = complexity_data.get("complexity", "SIMPLE").upper()
            archetype = complexity_data.get("archetype", "").upper()
        except:
            problem_complexity = "SIMPLE"
            archetype = "SEQUENTIAL"

        if problem_complexity == "COMPLEX":
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction=f"""Break down this {archetype} problem into atomic subproblems. Each subproblem should:
                - Be solvable independently or with specified dependencies
                - Have clear input/output
                - Maintain unit consistency
                - Include any necessary unit conversions
                Return as list of subproblems with dependencies.""",
                context=refined_schema
            )

            # Solve subproblems in parallel where possible
            async def solve_subproblem(sp):
                # Extract subproblem description
                sp_desc = sp.get('description', '')
                sp_id = sp.get('id', '')
                
                # Generate solution approach for this subproblem
                approach = await self.generate(
                    instruction=f"""For subproblem {sp_id}: {sp_desc}
                    Based on the overall schema: {refined_schema}
                    Generate precise mathematical approach. Specify:
                    - Formula to use
                    - Variables and their values
                    - Unit handling
                    - Expected output format""",
                    context=refined_schema
                )
                
                # Execute computation
                result = await self.programmer(
                    instruction=f"""Implement solution for subproblem {sp_id}.
                    APPROACH: {approach}
                    SCHEMA: {refined_schema}
                    Requirements:
                    - Use precise arithmetic
                    - Handle units correctly
                    - Validate result against real-world constraints
                    - Return ONLY the numerical result with unit if applicable""",
                    context=approach,
                    max_retries=3
                )
                return {"id": sp_id, "result": result, "description": sp_desc}

            # Execute subproblems respecting dependencies would require topological sort, 
            # but for simplicity we'll run all and let dependencies be handled by context
            # In production, you'd implement dependency resolution
            subproblem_results = await asyncio.gather(
                *[solve_subproblem(sp) for sp in subproblems]
            )

            # Synthesize final answer from subproblem results
            synthesis_context = "\n".join([f"{r['id']}: {r['result']} ({r['description']})" for r in subproblem_results])
            final_answer = await self.generate(
                instruction=f"""Synthesize final answer from subproblem results:
                {synthesis_context}
                
                Overall schema: {refined_schema}
                Combine results according to problem requirements. Ensure:
                - Correct mathematical combination of sub-results
                - Final unit is appropriate
                - Answer is single numerical value as required
                Return ONLY the final numerical answer.""",
                context=synthesis_context
            )

        else:
            # Simple/Moderate problem - direct solution
            # Generate three parallel solution attempts using different strategies
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""ALGEBRAIC APPROACH: 
                    Schema: {refined_schema}
                    Define variables, set up equations, solve systematically.
                    Show all steps. Return final numerical answer.""",
                    context=refined_schema
                ),
                self.generate(
                    instruction=f"""ARITHMETIC APPROACH:
                    Schema: {refined_schema}
                    Solve using step-by-step arithmetic operations without algebra.
                    Show calculations. Return final numerical answer.""",
                    context=refined_schema
                ),
                self.generate(
                    instruction=f"""UNIT ANALYSIS APPROACH:
                    Schema: {refined_schema}
                    Solve by tracking units through dimensional analysis.
                    Show unit conversions and cancellations. Return final numerical answer.""",
                    context=refined_schema
                )
            )

            # Use ensemble to select best answer
            final_answer = await self.ensemble(
                instruction="""Select the most accurate and logically sound answer from the three attempts.
                Criteria:
                1. Mathematical correctness
                2. Unit consistency
                3. Adherence to real-world constraints
                4. Clarity of reasoning
                If all agree, return any. If conflict, choose the one with most rigorous validation.
                Return ONLY the final numerical value.""",
                contexts_list=solution_attempts
            )

        # STEP 5: Final validation and refinement
        validated_answer = await self.revise(
            instruction=f"""Validate final answer: {final_answer}
            Against original problem and schema: {refined_schema}
            Check:
            - Does it answer the actual question asked?
            - Is it in correct units?
            - Does it satisfy real-world constraints (non-negative, integer if required)?
            - Is precision appropriate (integer vs decimal)?
            If any issue, correct it. Return ONLY the final numerical value.""",
            context=final_answer
        )

        # Extract just the numerical value (remove any explanatory text)
        # This is a simple fallback - in production you'd use more robust parsing
        import re
        match = re.search(r'[\d\.]+', validated_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (let evaluation handle it)
            return validated_answer.strip()