# Workflow ID: limr_15_0
# Benchmark: limr
# Data Indices: [175, 38]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
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
        """
        Universal workflow for LIMR mathematical reasoning problems.
        Architecture: Adaptive Diamond with Meta-Cognitive Feedback
        """
        import asyncio
        import re

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGIC DECOMPOSITION
        classification = await self.generate(
            instruction="""Perform deep semantic classification of this mathematical problem. Analyze:

1. Primary domain (geometry, number theory, combinatorics, algebra, probability, etc.)
2. Key mathematical structures (symmetries, invariants, recursions, transformations)
3. Signature patterns suggesting solution approaches (e.g., cyclic symmetry → roots of unity, functional equations → substitution patterns)
4. Expected answer constraints (integer 000-999, implies modular arithmetic or counting)
5. Potential pitfalls or non-obvious insights required

Output structured analysis with clear section headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction=f"""Based on classification:
{classification}

Decompose into 3-5 conceptual subproblems that capture different reasoning dimensions. Each subproblem should:
- Represent a distinct mathematical perspective (e.g., geometric, algebraic, combinatorial)
- Be solvable independently but contribute to overall solution
- Include built-in validation criteria (e.g., "result must be positive integer")
- Reference relevant theorems or techniques

Format as numbered subproblems with clear dependencies if any.""",
            context=classification
        )

        # PHASE 2: PARALLEL PERSPECTIVE GENERATION (DIAMOND FORK)
        perspective_tasks = []
        for i, subproblem in enumerate(decomposition):
            sub_id = subproblem.get('id', f'sub{i+1}')
            sub_desc = subproblem.get('description', '')
            
            # Generate perspective-specific instruction
            perspective_instruction = f"""Solve subproblem from perspective: {sub_desc}

Guidelines:
1. Use techniques appropriate to this perspective (e.g., coordinate geometry for spatial problems)
2. Include step-by-step reasoning with clear justifications
3. Validate intermediate results against problem constraints
4. If stuck, propose alternative approaches within this perspective
5. Final output should be numerical or lead to numerical result

Classification context: {classification[:500]}..."""
            
            task = self.generate(
                instruction=perspective_instruction,
                context=sub_desc
            )
            perspective_tasks.append(task)

        # Execute in parallel
        perspectives = await asyncio.gather(*perspective_tasks)

        # PHASE 3: VALIDATION & REFINEMENT
        validated_perspectives = []
        for i, perspective in enumerate(perspectives):
            # Self-validate each perspective
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution perspective:

1. Check mathematical consistency and logical flow
2. Verify all steps follow from premises
3. Confirm final result is integer 000-999 if applicable
4. Identify any gaps, errors, or unverified assumptions
5. Suggest specific improvements

Perspective: {perspective[:1000]}...""",
                context=perspective
            )
            
            # Revise if issues found
            if any(phrase in validation.lower() for phrase in ['error', 'gap', 'inconsistency', 'assumption']):
                revised = await self.revise(
                    instruction=f"""Improve based on validation feedback:
{validation}

Requirements:
- Fix identified issues
- Strengthen justifications
- Maintain perspective-specific approach
- Ensure numerical result is derivable""",
                    context=perspective
                )
                validated_perspectives.append(revised)
            else:
                validated_perspectives.append(perspective)

        # PHASE 4: SYNTHESIS & CONFLICT RESOLUTION (DIAMOND MERGE)
        synthesis = await self.ensemble(
            instruction=f"""Synthesize all perspectives into unified solution:

1. Identify agreements and contradictions between perspectives
2. Resolve conflicts by:
   - Checking against problem constraints
   - Evaluating mathematical rigor
   - Preferring approaches with explicit verification
3. Combine complementary insights
4. Extract final numerical answer (000-999)
5. Justify why this answer is correct and others are wrong if applicable

Classification context: {classification[:300]}...
Decomposition: {[d.get('description', '')[:100] for d in decomposition]}""",
            contexts_list=validated_perspectives
        )

        # PHASE 5: COMPUTATIONAL VERIFICATION (IF APPLICABLE)
        # Check if synthesis suggests computable verification
        needs_computation = await self.generate(
            instruction=f"""Determine if final answer can/should be verified computationally:

Analyze:
- Are there explicit calculations that can be coded?
- Can edge cases or small instances be tested?
- Would numerical simulation confirm result?

If yes, describe specific computation needed. If no, state "NO COMPUTATION NEEDED".

Synthesis: {synthesis[:500]}...""",
            context=synthesis
        )

        final_answer = synthesis
        if "NO COMPUTATION NEEDED" not in needs_computation.upper():
            try:
                computation = await self.programmer(
                    instruction=f"""Implement verification based on:
{needs_computation}

Requirements:
- Code must be self-contained and executable
- Output must be integer 000-999
- Include comments explaining mathematical basis
- Handle edge cases if mentioned in synthesis

Synthesis context: {synthesis[:800]}...""",
                    context=needs_computation,
                    max_retries=2
                )
                
                # Ensemble between analytical and computational results
                final_answer = await self.ensemble(
                    instruction="""Reconcile analytical solution with computational verification:

1. If they agree, output combined result
2. If they disagree, identify source of discrepancy
3. Determine which is more reliable based on:
   - Mathematical rigor
   - Computational precision
   - Problem constraints
4. Output final integer answer 000-999 with justification""",
                    contexts_list=[synthesis, computation]
                )
            except Exception:
                # Fallback to analytical solution if computation fails
                pass

        # PHASE 6: FINAL VALIDATION & FORMATTING
        final_validation = await self.revise(
            instruction="""Final validation and formatting:

1. Ensure answer is integer between 000 and 999
2. Remove all non-essential text - output ONLY the 3-digit integer
3. If multiple candidates, select most rigorously justified
4. If no clear answer, output 000 (default)

Format: Exactly three digits, zero-padded if necessary (e.g., 042, not 42)""",
            context=final_answer
        )

        # Extract exactly 3-digit integer using regex as safety net
        match = re.search(r'\b(\d{3})\b', final_validation)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and format to 3 digits
            numbers = re.findall(r'\d+', final_validation)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"{num:03d}"
            else:
                return "000"  # Ultimate fallback