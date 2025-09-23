# Workflow ID: limr_152_0
# Benchmark: limr
# Data Indices: [60, 154]

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

        # PHASE 1: META-ANALYSIS & STRATEGY CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical competition problem. Your response must include:

1. DOMAIN CLASSIFICATION: Identify primary mathematical domain (e.g., combinatorics, number theory, geometry, algebra, optimization) and secondary domains if applicable.

2. CONSTRAINT MAPPING: List all explicit and implicit constraints. Categorize them as: 
   - Structural (e.g., "exactly one per row/column")
   - Numerical (e.g., "answer between 000-999")
   - Logical (e.g., "no repeated flavors")

3. SOLUTION PARADIGM DETECTION: Determine whether this is primarily:
   - An optimization problem (min/max)
   - An enumeration problem (counting)
   - A proof/existence problem
   - A construction problem

4. STRATEGIC OPTIONS: Propose 3 distinct high-level solution approaches with their:
   - Core insight or transformation
   - Expected computational complexity
   - Key risks or failure modes
   - Alignment with problem constraints

Structure your response with clear section headers. Be brutally honest about what makes this problem difficult.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION & DECOMPOSITION
        # Run decomposition and strategy generation in parallel
        decomposition_task = self.decompose(
            instruction="""Break this problem into logically ordered subproblems. For each subproblem:
- Provide a clear, self-contained description
- Specify prerequisite subproblems by ID
- Indicate whether it requires symbolic reasoning, computation, or both
- Estimate complexity (low/medium/high)

Focus on creating a dependency graph that reveals the problem's inherent structure. Prioritize steps that reduce the solution space or expose invariants.""",
            context=problem_analysis
        )

        strategy_sketches_task = asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis: {problem_analysis[:1000]}

Develop a detailed ALGEBRAIC/ANALYTIC solution sketch. Focus on:
- Variable definitions and equation setup
- Key transformations or substitutions
- Theoretical bounds or invariants
- Potential simplification through symmetry or duality
- How to handle edge cases

Do NOT compute final answer yet. Output should be a reasoning roadmap.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the analysis: {problem_analysis[:1000]}

Develop a detailed COMBINATORIAL/ENUMERATIVE solution sketch. Focus on:
- Counting principles or probability frameworks
- Case decomposition or recursive structure
- Generating functions or combinatorial identities
- Symmetry exploitation or Burnside's lemma applications
- Computational tractability of enumeration

Do NOT compute final answer yet. Output should be a reasoning roadmap.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the analysis: {problem_analysis[:1000]}

Develop a detailed ALGORITHMIC/COMPUTATIONAL solution sketch. Focus on:
- Data structures needed (matrices, graphs, etc.)
- Algorithm selection (dynamic programming, greedy, etc.)
- Complexity analysis and optimization opportunities
- Early termination conditions or pruning strategies
- Precision handling for exact integer output

Do NOT compute final answer yet. Output should be a reasoning roadmap.""",
                context=""
            )
        )

        # Await parallel results
        decomposition, strategy_sketches = await asyncio.gather(
            decomposition_task, 
            strategy_sketches_task
        )
        algebraic_sketch, combinatorial_sketch, algorithmic_sketch = strategy_sketches

        # PHASE 3: SYNTHESIZE EXECUTION PLAN
        execution_plan = await self.ensemble(
            instruction="""You are given:
1. A decomposition of the problem into subproblems with dependencies
2. Three strategic solution sketches (algebraic, combinatorial, algorithmic)

Your task: Synthesize these into a unified, executable step-by-step plan. Rules:
- Respect the dependency graph from decomposition
- For each subproblem, select the most appropriate strategy (or hybrid)
- Specify for each step: 
   a) What to compute/derive
   b) Which operator to use (Generate, Revise, Programmer)
   c) Expected output format
   d) Validation criteria
- Include explicit verification steps for critical junctures
- Ensure final output is an integer 000-999

Output format: Numbered steps with clear headings. Be ruthlessly practical.""",
            contexts_list=[str(decomposition), algebraic_sketch, combinatorial_sketch, algorithmic_sketch]
        )

        # PHASE 4: DYNAMIC EXECUTION WITH VERIFICATION
        current_context = execution_plan
        final_answer = None
        verification_attempts = 0
        max_verification_attempts = 3

        while verification_attempts < max_verification_attempts:
            # Execute plan step by step (simplified here - in practice would parse and execute each step)
            # For this implementation, we'll use the plan to guide a focused Programmer call
            solution_attempt = await self.programmer(
                instruction=f"""Execute the following plan to solve the problem:

{execution_plan[:2000]}

Requirements:
- Implement the most computationally tractable approach from the plan
- Handle all edge cases mentioned in the problem analysis
- Return ONLY the final integer answer (000-999 format)
- Include brief comments explaining key steps
- If multiple approaches are viable, implement the one with lowest computational complexity

IMPORTANT: Your code must be self-contained and handle all input parsing from the original problem.""",
                context=current_context
            )

            # Extract potential answer
            answer_match = re.search(r'\b(?:000|[0-9]{1,3})\b', solution_attempt)
            if answer_match:
                candidate_answer = answer_match.group(0).zfill(3)
                
                # Verification step
                verification = await self.generate(
                    instruction=f"""Adversarial validation of candidate answer {candidate_answer}:

1. ASSUME THIS ANSWER IS WRONG. What is the most likely error source?
2. Check against original constraints: {problem_analysis[:500]}
3. Verify dimensional consistency (if applicable)
4. Test with simplified case or boundary condition
5. Cross-validate with alternative approach from unused strategy sketch

Output: "VERIFIED" if answer passes all checks, otherwise detailed error analysis.""",
                    context=f"Solution attempt: {solution_attempt}\n\nExecution plan: {execution_plan}"
                )

                if "VERIFIED" in verification.upper():
                    final_answer = candidate_answer
                    break
                else:
                    # Revise based on verification feedback
                    current_context = await self.revise(
                        instruction=f"""Revise the solution approach based on this verification feedback:

{verification}

Specifically:
- Address the identified error sources
- Strengthen weak points in logic or computation
- Consider alternative strategies from unused sketches
- Ensure output format compliance (000-999 integer)

Output revised execution plan or direct solution approach.""",
                        context=current_context
                    )
                    verification_attempts += 1
            else:
                # No answer extracted - revise approach
                current_context = await self.revise(
                    instruction="""No valid answer (000-999 integer) was extracted from the solution attempt. 
Possible issues:
- Code didn't execute correctly
- Answer not properly formatted
- Solution approach fundamentally flawed

Revise the entire approach. Consider:
- Switching to a different strategy from the original sketches
- Breaking problem into smaller computational steps
- Adding explicit output formatting in code
- Using symbolic computation first, then numerical evaluation

Output revised plan or direct solution approach.""",
                    context=current_context
                )
                verification_attempts += 1

        # PHASE 5: FINAL ENSEMBLE & OUTPUT
        if final_answer is None:
            # Fallback: ensemble all attempts
            final_synthesis = await self.ensemble(
                instruction="""Multiple solution attempts have been made. Synthesize the most reliable answer:

1. Compare all attempted solutions and their verification reports
2. Identify consensus or most rigorously verified result
3. If no clear winner, select the answer that best satisfies:
   - Original problem constraints
   - Mathematical consistency
   - Computational plausibility
4. Format as 3-digit integer (000-999)

Output ONLY the 3-digit integer, nothing else.""",
                contexts_list=[solution_attempt, verification, current_context, problem_analysis]
            )
            
            # Extract final answer
            final_match = re.search(r'\b(?:000|[0-9]{1,3})\b', final_synthesis)
            final_answer = final_match.group(0).zfill(3) if final_match else "000"

        return final_answer