# Workflow ID: limr_47_0
# Benchmark: limr
# Data Indices: [161, 25]

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

        # === PHASE 1: META-COGNITIVE CLASSIFICATION & STRATEGY SELECTION ===
        problem_analysis = await self.generate(
            instruction="""Perform deep problem classification and strategy mapping. Analyze:

1. Problem Type: Is this primarily combinatorial, probabilistic, algebraic, geometric, or number-theoretic? 
2. Solution Nature: Are we constructing a value, proving existence, optimizing, or counting?
3. Key Constraints: What explicit/implicit boundaries exist (e.g., integer answers, positivity, modular conditions)?
4. Known Techniques: What theorems, identities, or standard methods likely apply (e.g., stars and bars, inclusion-exclusion, generating functions)?
5. Complexity Estimate: How many distinct reasoning steps are required? Are there hidden subproblems?
6. Risk Factors: What are the most likely sources of error (e.g., off-by-one, misapplied formula, overlooked constraint)?

Output a structured JSON with keys: "type", "strategy_candidates", "constraints", "complexity", "risks".""",
            context=""
        )

        # Extract classification for dynamic routing
        classification = await self.programmer(
            instruction="""Parse the following analysis into a clean JSON object. Ensure all fields are present:
{
    "type": "string",
    "strategy_candidates": ["string"],
    "constraints": ["string"],
    "complexity": "integer",
    "risks": ["string"]
}
Return only the JSON object, no additional text.""",
            context=problem_analysis
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION ===
        decomposition_plan = await self.decompose(
            instruction=f"""Decompose this problem into minimal atomic subproblems. Guidelines:
- Each subproblem must be solvable independently or with specified dependencies.
- Prioritize logical flow: foundational results before dependent ones.
- Include verification subproblems (e.g., "validate intermediate result X").
- For probabilistic/combinatorial problems, separate counting from probability calculation.
- For algebraic problems, separate equation setup from solving.

Classification context: {classification}

Output as list of dicts with 'id', 'description', 'dependencies'.""",
            context=""
        )

        # Solve subproblems in topological order (respecting dependencies)
        subproblem_results = {}
        solved_ids = set()
        
        # Simple topological sort (assuming no cycles)
        unsolved = {sp['id']: sp for sp in decomposition_plan}
        while unsolved:
            ready = [sp_id for sp_id, sp in unsolved.items() 
                    if all(dep in solved_ids for dep in sp.get('dependencies', '').split(',') if dep)]
            
            if not ready:
                break  # Circular dependency or missing deps (shouldn't happen)
            
            # Solve ready subproblems in parallel
            solving_tasks = []
            for sp_id in ready:
                sp = unsolved[sp_id]
                task = self.generate(
                    instruction=f"""Solve subproblem: {sp['description']}

Guidelines:
- Be precise and show key steps.
- If computational, use exact arithmetic.
- Reference only solved subproblems: {list(solved_ids)}.
- If stuck, state why and what's missing.

Classification context: {classification}""",
                    context=json.dumps(subproblem_results)
                )
                solving_tasks.append((sp_id, task))
            
            # Execute in parallel
            results = await asyncio.gather(*[task for _, task in solving_tasks])
            for (sp_id, _), result in zip(solving_tasks, results):
                subproblem_results[sp_id] = result
                solved_ids.add(sp_id)
                del unsolved[sp_id]

        # === PHASE 3: STRATEGY ENSEMBLE & DIVERGENT IDEATION ===
        # Generate 3 distinct solution approaches in parallel
        strategy_candidates = json.loads(classification)['strategy_candidates'][:3]  # Cap at 3 for efficiency
        strategy_tasks = []
        
        for i, strategy in enumerate(strategy_candidates):
            task = self.generate(
                instruction=f"""Develop a complete solution using this strategy: {strategy}

Requirements:
- Show all steps from first principles.
- Justify non-obvious moves.
- Box final answer as \\boxed{{}}.
- If computation needed, write pseudocode or describe algorithm.

Context: {json.dumps(subproblem_results)}""",
                context=""
            )
            strategy_tasks.append(task)
        
        # Add a "creative alternative" strategy regardless of classification
        creative_strategy = await self.generate(
            instruction="""Ignore previous classifications. Invent a radically different solution approach:
- Can you transform the problem into another domain? (e.g., geometry → algebra)
- Is there a symmetry, invariant, or duality to exploit?
- Can you use generating functions, recursion, or probabilistic method unexpectedly?
- Show complete derivation and final answer.""",
            context=json.dumps(subproblem_results)
        )
        strategy_tasks.append(creative_strategy)
        
        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # === PHASE 4: ADVERSARIAL VALIDATION & ENSEMBLE SELECTION ===
        # Validate each strategy with a "devil's advocate" critique
        validation_tasks = []
        for i, strategy_result in enumerate(strategy_results):
            critique = await self.generate(
                instruction=f"""Play devil's advocate. Critique this solution:
{strategy_result}

Check for:
- Logical gaps or unjustified assumptions
- Arithmetic/algebraic errors
- Violations of constraints from classification: {classification}
- Plausibility of final answer (e.g., probabilities in [0,1], counts non-negative)
- Alternative interpretations of the problem statement

Output critique as bullet points. If no issues, state "No significant issues found."""",
                context=""
            )
            validation_tasks.append((strategy_result, critique))
        
        # Revise each strategy based on its critique
        revised_strategies = []
        for strategy_result, critique in validation_tasks:
            if "no significant issues" not in critique.lower():
                revised = await self.revise(
                    instruction=f"""Revise this solution to address the critique:
Critique: {critique}

Requirements:
- Fix all identified issues.
- Maintain original strategy unless fundamentally flawed.
- Keep final answer boxed.
- Add verification step if possible.""",
                    context=strategy_result
                )
                revised_strategies.append(revised)
            else:
                revised_strategies.append(strategy_result)
        
        # Ensemble: Select best or synthesize
        final_answer = await self.ensemble(
            instruction="""Select the single best solution or synthesize a hybrid. Criteria:
1. Correctness: Must be logically watertight and satisfy all constraints.
2. Elegance: Prefer simpler, more insightful solutions.
3. Verification: Solutions with built-in checks (e.e., small-case validation) rank higher.
4. Consistency: If multiple solutions agree, that answer is preferred.

Extract the final integer answer (000-999) and output ONLY the integer, no explanation.""",
            contexts_list=revised_strategies
        )
        
        # === PHASE 5: COMPUTATIONAL VERIFICATION (if applicable) ===
        # Attempt to verify via code if the problem is computational
        try:
            verification_code = await self.programmer(
                instruction=f"""Write Python code to verify the answer {final_answer}. 
- Use exact integer/rational arithmetic.
- Handle edge cases.
- Output should be the computed answer (integer 0-999).
- If verification impossible (e.g., proof problem), output "N/A".

Classification: {classification}""",
                context=json.dumps(subproblem_results),
                max_retries=2
            )
            
            # If verification succeeded and matches, return it
            if verification_code.strip() != "N/A" and verification_code.strip().isdigit():
                verified_answer = int(verification_code.strip())
                if 0 <= verified_answer <= 999:
                    return f"{verified_answer:03d}"
        except:
            pass  # Fall back to ensemble answer if verification fails
        
        # Ensure final answer is 3-digit string
        try:
            answer_int = int(final_answer.strip())
            if 0 <= answer_int <= 999:
                return f"{answer_int:03d}"
        except:
            pass
            
        # Fallback: Extract any integer from the ensemble result
        import re
        digits = re.findall(r'\b\d{1,3}\b', final_answer)
        for d in digits:
            if 0 <= int(d) <= 999:
                return f"{int(d):03d}"
        
        # Ultimate fallback
        return "000"