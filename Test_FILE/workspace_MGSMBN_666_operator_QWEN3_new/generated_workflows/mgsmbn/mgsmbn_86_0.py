# Workflow ID: mgsmbn_86_0
# Benchmark: mgsmbn
# Data Indices: [180, 188]

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

        # === PHASE 1: PARALLEL SEMANTIC DECOMPOSITION ===
        # Extract problem structure through three independent lenses
        math_analysis, narrative_analysis, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform mathematical entity extraction:
                - Identify all numerical values and their meanings
                - Extract explicit and implicit operations (add, multiply, divide, etc.)
                - Map relationships between quantities (e.g., 'twice as much', 'one-third of')
                - Identify the unknown to solve for
                Format as structured JSON with keys: numbers, operations, relationships, unknown""",
                context=""
            ),
            self.generate(
                instruction="""Perform narrative decomposition:
                - Identify all actors (people, companies, objects)
                - Extract sequence of events or actions
                - Note temporal markers (first year, then, daily, weekly)
                - Identify cause-effect or dependency chains
                Format as structured JSON with keys: actors, events, sequence, dependencies""",
                context=""
            ),
            self.generate(
                instruction="""Perform constraint and unit analysis:
                - Identify all units (টাকা, ঘণ্টা, টমেটো, লতা, etc.)
                - Extract implicit constraints (must be integer, non-negative, etc.)
                - Note boundary conditions or real-world limitations
                - Identify any conversion requirements
                Format as structured JSON with keys: units, constraints, boundaries, conversions""",
                context=""
            )
        )

        # === PHASE 2: SYNTHESIZE UNIFIED PROBLEM MODEL ===
        unified_model = await self.ensemble(
            instruction="""Synthesize a unified problem model from three perspectives:
            1. Mathematical entities and relationships
            2. Narrative structure and event sequence
            3. Constraints, units, and boundary conditions
            
            Create a comprehensive problem representation that:
            - Integrates all numerical values with their contextual meanings
            - Maps the chronological or logical flow of operations
            - Embeds all constraints and unit requirements
            - Clearly defines the unknown to solve for
            - Preserves all critical information from each perspective
            
            Output as well-structured JSON with keys: 
            problem_summary, entities, operations_sequence, constraints, target_unknown""",
            contexts_list=[math_analysis, narrative_analysis, constraint_analysis]
        )

        # === PHASE 3: PROBLEM TYPE CLASSIFICATION & STRATEGY SELECTION ===
        strategy_classification = await self.generate(
            instruction=f"""Based on the unified problem model:
            {unified_model}
            
            Classify the problem and select solution strategy:
            1. Problem Type: [Sequential, Proportional, Distribution, Rate, Comparison, Multi-entity]
            2. Computational Depth: [Single-step, Multi-step, Hierarchical]
            3. Required Precision: [Exact integer, Exact decimal, Estimation acceptable]
            4. Recommended Approach: [Direct calculation, Algebraic modeling, Iterative simulation, Decomposition needed]
            5. Potential Pitfalls: [Unit conversion, Hidden steps, Fractional intermediates, Integer constraints]
            
            Output as JSON with these keys.""",
            context=unified_model
        )

        # === PHASE 4: ADAPTIVE SOLUTION PATH ===
        classification_data = json.loads(strategy_classification)
        
        if classification_data.get("Recommended Approach") == "Decomposition needed":
            # Hierarchical problem - break into subproblems
            subproblems = await self.decompose(
                instruction=f"""Decompose this problem into solvable subproblems:
                Problem Model: {unified_model}
                Classification: {strategy_classification}
                
                Create dependency-ordered subproblems that:
                - Each can be solved independently once dependencies are met
                - Collectively lead to the final answer
                - Respect unit and constraint requirements
                - Handle hidden steps explicitly
                
                Return list of subproblems with IDs and dependencies.""",
                context=unified_model
            )
            
            # Solve subproblems in dependency order (simplified for demo - in practice, topological sort)
            subproblem_results = {}
            for sp in subproblems:
                sp_id = sp["id"]
                sp_desc = sp["description"]
                deps = sp.get("dependencies", "").split(",") if sp.get("dependencies") else []
                
                # Wait for dependencies (simplified - assumes linear order)
                dep_context = "\n".join([f"{dep_id}: {subproblem_results.get(dep_id, '')}" for dep_id in deps if dep_id])
                
                # Generate symbolic representation
                symbolic_form = await self.generate(
                    instruction=f"""Convert to executable mathematical form:
                    Subproblem: {sp_desc}
                    Dependencies: {dep_context}
                    Constraints: {strategy_classification}
                    
                    Express as equation or algorithm. Specify variables, operations, and units.
                    If multiple approaches possible, choose the most straightforward.""",
                    context=dep_context
                )
                
                # Refine for unit consistency and constraints
                refined_form = await self.revise(
                    instruction=f"""Refine for correctness and constraints:
                    - Ensure unit consistency throughout
                    - Apply boundary conditions (e.g., integer results where required)
                    - Verify operation order matches problem chronology
                    - Add any missing implicit steps
                    - Format for direct code translation""",
                    context=symbolic_form
                )
                
                # Execute
                result = await self.programmer(
                    instruction=f"""Execute this subproblem:
                    Problem: {sp_desc}
                    Mathematical Form: {refined_form}
                    Constraints: {strategy_classification}
                    
                    Return only the numerical result with appropriate precision.""",
                    context=refined_form
                )
                subproblem_results[sp_id] = result
            
            # Final assembly (simplified - assumes last subproblem is final answer)
            final_answer = subproblem_results.get(subproblems[-1]["id"], "0")
            
        else:
            # Direct solution path
            # Generate symbolic representation
            symbolic_form = await self.generate(
                instruction=f"""Convert problem to executable mathematical form:
                Unified Model: {unified_model}
                Strategy: {strategy_classification}
                
                Express as equation or algorithm. Specify:
                - Variables and their meanings
                - Sequence of operations
                - Unit handling
                - Final output format
                If multiple approaches, choose most direct.""",
                context=unified_model
            )
            
            # Refine for unit consistency and constraints
            refined_form = await self.revise(
                instruction=f"""Refine for correctness:
                - Ensure unit consistency
                - Apply real-world constraints (integer results, non-negative, etc.)
                - Verify operation order
                - Add any missing implicit steps
                - Format for direct code execution
                - Include validation checks within the code""",
                context=symbolic_form
            )
            
            # Generate multiple solution approaches in parallel
            approach1, approach2 = await asyncio.gather(
                self.programmer(
                    instruction=f"""Solve using direct calculation approach:
                    Mathematical Form: {refined_form}
                    Constraints: {strategy_classification}
                    Return only numerical result.""",
                    context=refined_form
                ),
                self.programmer(
                    instruction=f"""Solve using algebraic modeling approach:
                    Mathematical Form: {refined_form}
                    Constraints: {strategy_classification}
                    Return only numerical result.""",
                    context=refined_form
                )
            )
            
            # Ensemble to select best answer
            final_answer = await self.ensemble(
                instruction=f"""Select the correct answer:
                Approach 1 Result: {approach1}
                Approach 2 Result: {approach2}
                Problem Constraints: {strategy_classification}
                
                Choose the answer that:
                - Matches all problem constraints
                - Is mathematically consistent
                - Aligns with real-world plausibility
                - If both valid, prefer simpler approach
                Return ONLY the numerical value.""",
                contexts_list=[approach1, approach2]
            )

        # === PHASE 5: VALIDATION & REFINEMENT LOOP ===
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate answer against original problem:
                Original Problem: {self.problem_text}
                Current Answer: {final_answer}
                Problem Model: {unified_model}
                Constraints: {strategy_classification}
                
                Check:
                1. Does answer satisfy all stated conditions?
                2. Are units and precision appropriate?
                3. Is the answer plausible in real-world context?
                4. Were all steps and dependencies accounted for?
                
                If valid, respond 'VALID'. If invalid, explain exactly what's wrong.""",
                context=final_answer
            )
            
            if "VALID" in validation.upper():
                break
            else:
                # Revise and recalculate
                revised_form = await self.revise(
                    instruction=f"""Fix based on validation feedback:
                    Validation Feedback: {validation}
                    Previous Mathematical Form: {refined_form}
                    Problem Model: {unified_model}
                    
                    Correct the mathematical representation and ensure all constraints are met.""",
                    context=refined_form
                )
                
                final_answer = await self.programmer(
                    instruction=f"""Recalculate with corrected form:
                    Mathematical Form: {revised_form}
                    Constraints: {strategy_classification}
                    Return only numerical result.""",
                    context=revised_form
                )

        # Extract and return clean numerical answer
        clean_answer = await self.generate(
            instruction=f"""Extract final numerical answer:
            Current Output: {final_answer}
            Ensure it's a clean number (integer or decimal) with no text.
            If multiple numbers, pick the final answer.
            Remove any units or explanatory text.""",
            context=final_answer
        )
        
        return clean_answer.strip()