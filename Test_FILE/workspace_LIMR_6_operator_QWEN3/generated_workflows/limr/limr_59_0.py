# Workflow ID: limr_59_0
# Benchmark: limr
# Data Indices: [84, 206]

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

        # PHASE 1: COGNITIVE TRIAGE — PARALLEL PROBLEM CHARACTERIZATION
        classification_tasks = [
            self.generate(
                instruction="""Perform deep structural analysis of the mathematical problem:
                1. Identify all mathematical objects (polynomials, sequences, geometric entities, etc.)
                2. Classify the primary domain (algebra, number theory, combinatorics, geometry, etc.)
                3. Extract explicit constraints and implicit assumptions
                4. Note any symmetries, invariants, or special properties
                5. Predict potential solution strategies (symbolic manipulation, computational enumeration, theorem application, etc.)
                Format as a structured JSON-like analysis with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Perform strategic meta-analysis:
                1. What level of mathematical sophistication is required? (Olympiad, undergraduate, research-level)
                2. Are there known theorems or identities likely to be relevant?
                3. What are the potential pitfalls or common mistakes for this problem type?
                4. What form should the final answer take? (integer, fraction, expression, etc.)
                5. Estimate the number of non-trivial steps required.
                Provide a concise but comprehensive strategic assessment.""",
                context=""
            ),
            self.generate(
                instruction="""Perform tactical decomposition preview:
                Without fully solving, outline potential subproblems or milestones:
                1. What intermediate results must be computed?
                2. Are there natural breaking points in the reasoning chain?
                3. What dependencies exist between components?
                4. Which parts might benefit from computational verification?
                Present as a numbered list of tactical waypoints.""",
                context=""
            )
        ]
        
        classification_results = await asyncio.gather(*classification_tasks)
        
        # PHASE 2: STRATEGY SYNTHESIS — ENSEMBLE-BASED PLANNING
        strategy_profile = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified solution strategy profile:
            1. Consolidate domain classification and required techniques
            2. Prioritize solution approaches based on predicted efficiency and reliability
            3. Identify which components should be handled symbolically vs. computationally
            4. Flag high-risk steps requiring extra verification
            5. Recommend operator sequence and parallelization opportunities
            Output a detailed execution plan with rationale for each decision.""",
            contexts_list=classification_results
        )

        # PHASE 3: ADAPTIVE EXECUTION — CONDITIONAL BRANCHING
        # Dynamically construct decomposition based on strategy profile
        decomposition_plan = await self.generate(
            instruction=f"""Based on the strategy profile:
            {strategy_profile}
            
            Generate a detailed decomposition plan with:
            1. Specific subproblems with clear success criteria
            2. Dependencies between subproblems
            3. Recommended operator for each subproblem (generate, revise, programmer, etc.)
            4. Verification checkpoints
            Format as a JSON-parseable list of subproblem objects with 'id', 'description', 'operator', 'dependencies'.""",
            context=strategy_profile
        )

        # Parse decomposition (with fallback)
        try:
            subproblems = json.loads(decomposition_plan)
        except:
            # Fallback: use generic decomposition
            subproblems_raw = await self.decompose(
                instruction="Break this problem into logically independent subproblems with clear dependencies. Focus on mathematical milestones rather than procedural steps.",
                context=""
            )
            # Convert to consistent format
            subproblems = [
                {
                    "id": sp["id"],
                    "description": sp["description"],
                    "operator": "generate",  # default
                    "dependencies": sp.get("dependencies", "").split(",") if sp.get("dependencies") else []
                }
                for sp in subproblems_raw
            ]

        # Execute subproblems with dependency resolution
        results = {}
        completed = set()
        
        # Simple topological sort execution
        while len(completed) < len(subproblems):
            executable = [
                sp for sp in subproblems 
                if sp["id"] not in completed and 
                all(dep.strip() in completed for dep in sp["dependencies"] if dep.strip())
            ]
            
            if not executable:
                break  # Circular dependency or error
                
            # Execute executable subproblems in parallel
            sub_results = await asyncio.gather(*[
                self._execute_subproblem(sp, results)
                for sp in executable
            ])
            
            # Store results
            for sp, result in zip(executable, sub_results):
                results[sp["id"]] = result
                completed.add(sp["id"])

        # PHASE 4: VALIDATION CASCADE — PARALLEL VERIFICATION
        verification_tasks = []
        
        # Re-expression verification
        verification_tasks.append(
            self.generate(
                instruction=f"""Re-express the original problem in an alternative mathematical framework and verify the solution:
                Original problem: {self.problem_text}
                Proposed solution: {json.dumps(results)}
                1. Choose a different mathematical perspective (e.g., modular arithmetic for algebra, coordinate geometry for synthetic, etc.)
                2. Derive the solution independently using this new framework
                3. Compare results and note any discrepancies
                4. Resolve conflicts if found""",
                context=json.dumps(results)
            )
        )
        
        # Edge case verification
        verification_tasks.append(
            self.generate(
                instruction=f"""Test the solution against edge cases and boundary conditions:
                1. Identify critical edge cases for this problem type
                2. Apply the solution to these cases
                3. Verify consistency and correctness
                4. Flag any failures or inconsistencies""",
                context=json.dumps(results)
            )
        )
        
        # Simplification verification
        verification_tasks.append(
            self.generate(
                instruction=f"""Create a simplified version of the problem and verify the solution scales appropriately:
                1. Reduce complexity (smaller numbers, fewer variables, simpler constraints)
                2. Solve the simplified version independently
                3. Check if the full solution reduces correctly to the simplified case
                4. Note any scaling inconsistencies""",
                context=json.dumps(results)
            )
        )
        
        verification_results = await asyncio.gather(*verification_tasks)
        
        # PHASE 5: CONFLICT RESOLUTION & FINAL SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""Synthesize all solution attempts and verification results into a final answer:
            1. Compare all solution paths and verification outcomes
            2. Resolve any discrepancies through logical reconciliation
            3. Select the most robust and well-verified answer
            4. Format the final answer as a three-digit integer (000-999) as required
            5. Provide brief justification for the final selection
            Output ONLY the three-digit integer answer, nothing else.""",
            contexts_list=[json.dumps(results)] + verification_results
        )
        
        return final_answer.strip()

    async def _execute_subproblem(self, subproblem, existing_results):
        """Execute a single subproblem based on its specified operator"""
        context = "\n".join([
            f"Subproblem {subproblem['id']}: {subproblem['description']}",
            f"Existing results: {json.dumps(existing_results)}",
            f"Dependencies: {subproblem.get('dependencies', [])}"
        ])
        
        operator_name = subproblem.get("operator", "generate")
        
        if operator_name == "programmer":
            return await self.programmer(
                instruction=f"""Solve this mathematical subproblem computationally:
                {subproblem['description']}
                Requirements:
                - Use exact arithmetic (no floating point approximations)
                - Handle edge cases explicitly
                - Return only the final numerical result
                - If multiple results, return as comma-separated list""",
                context=context
            )
        elif operator_name == "revise":
            # Get the result to revise (from dependencies)
            target_id = subproblem.get("dependencies", [""])[0].strip() if subproblem.get("dependencies") else ""
            target_result = existing_results.get(target_id, "")
            return await self.revise(
                instruction=f"""Improve and verify this mathematical result:
                {subproblem['description']}
                Focus on:
                - Correcting any logical errors
                - Improving mathematical rigor
                - Adding missing steps or justifications
                - Ensuring alignment with problem constraints""",
                context=target_result
            )
        else:  # default to generate
            return await self.generate(
                instruction=f"""Solve this mathematical subproblem:
                {subproblem['description']}
                Requirements:
                - Show all key steps and reasoning
                - Justify non-obvious insights
                - Maintain mathematical precision
                - Return final result clearly marked""",
                context=context
            )