# Workflow ID: limr_55_0
# Benchmark: limr
# Data Indices: [337, 283]

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

        # PHASE 1: META-ANALYSIS & STRATEGY PROPOSAL
        strategy_analysis = await self.generate(
            instruction="""Perform a deep meta-analysis of this mathematical problem. Your task:

1. CLASSIFY the problem type with high precision: Is it Geometry, Number Theory, Algebra, Combinatorics, Probability, or Optimization? Consider subtypes (e.g., "Modular Arithmetic" under Number Theory).

2. IDENTIFY required mathematical techniques: List specific methods (e.g., "Chinese Remainder Theorem", "Inradius formula for right triangles", "Generating functions").

3. DETECT potential pitfalls or non-obvious insights: What might a solver miss? Are there redundant constraints? Hidden symmetries? Special cases?

4. PROPOSE 3 distinct high-level solution strategies. For each, outline:
   - Core approach (e.g., "Coordinate geometry", "Modular reduction", "Recursive counting")
   - Key steps involved
   - Why it might succeed or fail

5. FLAG if the problem requires proof, existence demonstration, or counterexample construction.

Output in structured JSON format with keys: "classification", "techniques", "pitfalls", "strategies", "special_requirements".""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXECUTION
        # Parse strategies (assume at least one, up to three)
        try:
            analysis_data = json.loads(strategy_analysis)
            strategies = analysis_data.get("strategies", [])[:3]  # Limit to 3
            if not strategies:
                strategies = ["Direct symbolic manipulation and computation"]
        except:
            # Fallback if JSON parsing fails
            strategies = ["Direct symbolic manipulation and computation"]

        async def execute_strategy(strategy_desc, index):
            """Execute one solution strategy end-to-end"""
            try:
                # Step 2a: Decompose strategy into subproblems
                decomposition = await self.decompose(
                    instruction=f"""Decompose the following solution strategy into atomic, ordered subproblems:

STRATEGY: {strategy_desc}

GUIDELINES:
- Each subproblem should be solvable independently or with specified dependencies.
- Include computational, symbolic, and verification steps.
- For geometry: include coordinate setup, distance/angle calculations, formula applications.
- For number theory: include modular reductions, equation setups, solution validations.
- For combinatorics: include case breakdowns, counting principles, summation setups.
- Output should be granular enough for step-by-step solving.""",
                    context=""
                )
                
                # Execute subproblems in dependency order
                subproblem_results = {}
                for sub in decomposition:
                    sub_id = sub['id']
                    deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
                    
                    # Wait for dependencies
                    dep_context = "\n".join([f"Subproblem {d}: {subproblem_results.get(d, 'Not solved yet')}" for d in deps if d in subproblem_results])
                    
                    # Solve subproblem
                    if "compute" in sub['description'].lower() or "calculate" in sub['description'].lower():
                        # Use programmer for computational steps
                        sub_result = await self.programmer(
                            instruction=f"""Solve this mathematical subproblem:

{sub['description']}

Use precise computation. Show code and output. If symbolic manipulation is needed first, do it in comments.
Context from previous steps:
{dep_context}""",
                            context=dep_context
                        )
                    else:
                        # Use generate for symbolic/logical steps
                        sub_result = await self.generate(
                            instruction=f"""Solve this mathematical subproblem through reasoning:

{sub['description']}

Show all steps. Be rigorous. Reference previous results if needed.
Context from previous steps:
{dep_context}""",
                            context=dep_context
                        )
                    
                    subproblem_results[sub_id] = sub_result
                
                # Assemble final answer from last subproblem (or synthesize)
                final_sub_id = decomposition[-1]['id'] if decomposition else "unknown"
                final_answer = subproblem_results.get(final_sub_id, "No solution generated")
                
                return f"""STRATEGY: {strategy_desc}

SOLUTION PATH:
{json.dumps(subproblem_results, indent=2)}

FINAL OUTPUT:
{final_answer}"""
                
            except Exception as e:
                return f"""STRATEGY: {strategy_desc}

EXECUTION FAILED: {str(e)}

FALLBACK: Attempting direct computation...

{await self.programmer(
    instruction="Solve the original problem with brute-force computation if applicable. Show all work.",
    context=""
)}"""

        # Run all strategies in parallel
        strategy_tasks = [execute_strategy(strat, i) for i, strat in enumerate(strategies)]
        strategy_results = await asyncio.gather(*strategy_tasks, return_exceptions=True)
        
        # Convert exceptions to error messages
        cleaned_results = []
        for res in strategy_results:
            if isinstance(res, Exception):
                cleaned_results.append(f"STRATEGY FAILED WITH EXCEPTION: {str(res)}")
            else:
                cleaned_results.append(str(res))

        # PHASE 3: ENSEMBLE SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction="""You are a senior mathematics competition judge. Evaluate the candidate solutions below:

1. ASSESS each solution for:
   - Correctness of reasoning
   - Completeness of steps
   - Handling of edge cases
   - Final answer validity

2. SELECT the single best solution OR synthesize a new solution by combining the strongest elements from multiple candidates.

3. ENSURE the final answer is an integer between 000 and 999 as required.

4. If all solutions are flawed, construct a new correct solution from first principles.

OUTPUT: The complete, correct solution with final answer clearly boxed.""",
            contexts_list=cleaned_results
        )

        # PHASE 4: VERIFICATION & REFINEMENT
        verified_solution = await self.revise(
            instruction="""You are a skeptical mathematician reviewing this solution. Your task:

1. ASSUME this solution contains at least one error. Find it.
2. Check all calculations, logical steps, and assumptions.
3. Verify the answer satisfies all original problem constraints.
4. If no error is found, confirm with "VERIFIED: No errors detected."
5. If errors are found, provide the corrected solution with detailed fixes.

Be ruthless. Mathematical precision is non-negotiable.""",
            context=synthesized_solution
        )

        # Optional second verification if first revision made major changes
        if "error" in verified_solution.lower() or "fix" in verified_solution.lower():
            double_verified = await self.revise(
                instruction="Final verification: Confirm this corrected solution is flawless. Output only the final answer if correct.",
                context=verified_solution
            )
            final_output = double_verified
        else:
            final_output = verified_solution

        # PHASE 5: ANSWER EXTRACTION
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final integer answer from the solution below. 

RULES:
- Answer must be an integer between 000 and 999.
- Remove all text, explanations, and units.
- If multiple answers, select the one that best fits the problem.
- If no clear answer, return "000".

Output format: exactly three digits (e.g., "123", "007", "999").""",
            context=final_output
        )

        return final_answer.strip()