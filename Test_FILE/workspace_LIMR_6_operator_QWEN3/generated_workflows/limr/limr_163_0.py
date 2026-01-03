# Workflow ID: limr_163_0
# Benchmark: limr
# Data Indices: [66, 195]

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

        # PHASE 1: META-CLASSIFICATION WITH CONFIDENCE SCORING
        classification = await self.generate(
            instruction="""Perform a deep diagnostic classification of this mathematical problem. You must:

1. Assign it to one primary domain: Geometry, Number Theory, Algebra, Combinatorics, or Optimization.
2. Identify secondary domains if applicable (e.g., "Algebra with Combinatorics").
3. List the core mathematical objects: polynomials, trigonometric functions, modular equations, recursive sequences, geometric figures, etc.
4. Predict the solution strategy: symbolic manipulation, case enumeration, coordinate transformation, generating functions, etc.
5. Estimate your confidence in this classification as a percentage (0-100%).
6. Flag any ambiguities or hybrid characteristics that might require parallel approaches.

Format your response EXACTLY as:
DOMAIN: [Primary Domain]
SECONDARY: [Secondary Domains or "None"]
OBJECTS: [Comma-separated list]
STRATEGY: [Predicted approach]
CONFIDENCE: [XX]%
AMBIGUITIES: [Description or "None"]""",
            context=""
        )

        # Extract confidence for branching
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)%', classification)
        confidence = int(confidence_match.group(1)) if confidence_match else 50

        # PHASE 2: DYNAMIC SUB-WORKFLOW SPAWNING
        if confidence >= 80:
            # High confidence: execute specialized sub-workflow
            solution_candidates = [await self.execute_specialized_workflow(classification)]
        else:
            # Low confidence: parallel exploration across likely domains
            domain_hints = await self.generate(
                instruction=f"""Given ambiguous classification:
{classification}

List 2-3 most plausible primary domains to explore in parallel. For each, describe a 1-sentence tailored strategy.
Format: 
- DOMAIN: Strategy
- DOMAIN: Strategy""",
                context=classification
            )
            
            domains = re.findall(r'-\s*DOMAIN:\s*([^\n]+)', domain_hints)
            solution_candidates = await asyncio.gather(
                *[self.execute_domain_strategy(domain.strip()) for domain in domains[:3]]
            )

        # PHASE 3: ADVERSARIAL VALIDATION & REFINEMENT
        validated_solutions = []
        for candidate in solution_candidates:
            for attempt in range(3):  # Max 3 refinement loops
                critique = await self.generate(
                    instruction=f"""Adversarially critique this solution attempt:
{candidate}

Assume it contains a subtle error. Check:
- Boundary conditions and domain restrictions
- Off-by-one errors in counting or indexing
- Precision loss in trigonometric or logarithmic calculations
- Misapplied identities or theorems
- Units or angle measure consistency (degrees vs radians)
- Integer constraint satisfaction (answer must be 000-999)

If no error found, state "VERIFIED". Otherwise, describe the most critical flaw.""",
                    context=candidate
                )
                
                if "VERIFIED" in critique.upper():
                    validated_solutions.append(candidate)
                    break
                else:
                    candidate = await self.revise(
                        instruction=f"""Revise the solution to fix this flaw:
{critique}

Incorporate the critique while preserving correct elements. Show corrected steps explicitly.""",
                        context=candidate
                    )
            else:
                # If still not verified, include with critique for ensemble
                validated_solutions.append(f"CANDIDATE WITH UNRESOLVED CRITIQUE:\n{critique}\n\nSOLUTION:\n{candidate}")

        # PHASE 4: CONSENSUS SYNTHESIS & INTEGER FINALIZATION
        if len(validated_solutions) == 1:
            final_answer = validated_solutions[0]
        else:
            final_answer = await self.ensemble(
                instruction="""Synthesize the most correct answer from these candidates. Consider:

1. Which solution has the most rigorous derivation?
2. Which survived adversarial critique with minimal revisions?
3. Which aligns best with the problem's domain classification?
4. Which produces an integer between 000 and 999?

If candidates conflict, perform a step-by-step reconciliation. Your final output must be a single integer (000-999) with a brief justification.""",
                contexts_list=validated_solutions
            )

        # Ensure final output is a clean integer
        integer_result = await self.programmer(
            instruction="""Extract the final integer answer from this text. The answer must be an integer between 000 and 999.

Steps:
1. Search for any 3-digit number or number that can be converted to 3-digit format.
2. If multiple numbers exist, select the one with mathematical justification.
3. If no number found, return 000 as fallback.
4. Output ONLY the 3-digit integer, zero-padded if necessary.

Example outputs: "123", "042", "007".""",
            context=final_answer
        )

        return integer_result.strip()

    async def execute_specialized_workflow(self, classification: str) -> str:
        """Execute domain-specialized workflow based on classification."""
        if "Combinatorics" in classification or "Probability" in classification:
            return await self.combinatorics_workflow()
        elif "Algebra" in classification or "Trigonometry" in classification:
            return await self.algebra_workflow()
        elif "Number Theory" in classification:
            return await self.number_theory_workflow()
        elif "Geometry" in classification:
            return await self.geometry_workflow()
        else:
            return await self.optimization_workflow()

    async def execute_domain_strategy(self, domain: str) -> str:
        """Generic domain execution for parallel exploration."""
        strategy_map = {
            "Combinatorics": self.combinatorics_workflow,
            "Algebra": self.algebra_workflow,
            "Number Theory": self.number_theory_workflow,
            "Geometry": self.geometry_workflow,
            "Optimization": self.optimization_workflow
        }
        
        for key, func in strategy_map.items():
            if key in domain:
                return await func()
        
        # Fallback: general generate
        return await self.generate(
            instruction="Solve using general mathematical reasoning. Show all steps.",
            context=""
        )

    async def combinatorics_workflow(self) -> str:
        initial = await self.generate(
            instruction="""Solve this combinatorics/probability problem. Strategy:

1. Identify total possible outcomes (denominator).
2. Identify favorable outcomes (numerator) - consider symmetry, complementary counting, or casework.
3. Express probability as reduced fraction if applicable.
4. Convert to required format (integer 000-999 may require multiplication or percentage conversion).

For grid problems: check horizontal, vertical, diagonal, and other linear patterns. Use coordinate geometry if needed.""",
            context=""
        )
        
        # Delegate exact computation to programmer
        computed = await self.programmer(
            instruction="""Implement exact combinatorial calculation based on this reasoning:
{reasoning}

Calculate numerator and denominator separately. Return probability as decimal or fraction, then convert to integer format as specified (e.g., multiply by 1000 for 3-digit representation if probability).""",
            context=initial
        )
        
        return await self.revise(
            instruction="Integrate computational result with reasoning. Ensure final answer is clearly stated.",
            context=f"{initial}\n\nCOMPUTATION RESULT:\n{computed}"
        )

    async def algebra_workflow(self) -> str:
        symbolic = await self.generate(
            instruction="""Solve this algebra/trigonometry problem. Strategy:

1. Simplify using identities (trig, polynomial, logarithmic).
2. Factor or substitute to reduce complexity.
3. Solve equation step-by-step, showing all manipulations.
4. Apply domain restrictions (e.g., 100° < x < 200°).
5. Sum or aggregate solutions as required.

For trig equations: use sum-to-product, double-angle, or symmetry identities before solving.""",
            context=""
        )
        
        # Use programmer for root finding or summation
        numeric = await self.programmer(
            instruction="""Given this algebraic/trigonometric derivation:
{derivation}

Implement numerical solution: find all roots in specified interval, sum them, or compute required aggregate. Return exact integer if possible, or precise decimal for conversion.""",
            context=symbolic
        )
        
        return await self.revise(
            instruction="Merge symbolic derivation with numerical result. Verify interval constraints and unit consistency.",
            context=f"{symbolic}\n\nNUMERIC RESULT:\n{numeric}"
        )

    async def number_theory_workflow(self) -> str:
        initial = await self.generate(
            instruction="""Solve this number theory problem. Strategy:

1. Factorize numbers or expressions.
2. Apply modular arithmetic or divisibility rules.
3. Solve Diophantine equations via parameterization or bounding.
4. Use prime factorization for counting or optimization.
5. Check small cases to identify patterns.

For modular problems: reduce modulo early and often. For Diophantine: bound variables then enumerate.""",
            context=""
        )
        
        refined = await self.revise(
            instruction="Strengthen number theory argument: add modular checks, verify edge cases, ensure integer constraints are satisfied.",
            context=initial
        )
        
        return refined

    async def geometry_workflow(self) -> str:
        coordinate_approach = await self.generate(
            instruction="""Convert this geometry problem to coordinate system. Strategy:

1. Assign coordinates to all points.
2. Express geometric conditions (collinearity, distance, angle) algebraically.
3. Solve system of equations.
4. Use vector cross products for collinearity or area calculations.

For grid problems: use integer coordinates and check slopes or vector alignments.""",
            context=""
        )
        
        computed = await self.programmer(
            instruction="""Implement coordinate geometry solution:
{approach}

Calculate exact values (distances, slopes, intersections). Return numerical result suitable for integer conversion.""",
            context=coordinate_approach
        )
        
        return await self.revise(
            instruction="Combine geometric reasoning with computational result. Ensure spatial logic matches algebraic output.",
            context=f"{coordinate_approach}\n\nCOMPUTATION:\n{computed}"
        )

    async def optimization_workflow(self) -> str:
        analysis = await self.generate(
            instruction="""Solve this optimization/sequence problem. Strategy:

1. Identify objective function and constraints.
2. Use calculus (derivatives) or discrete methods (AM-GM, Cauchy-Schwarz) for extrema.
3. For sequences: find pattern, derive closed form, or compute recursively.
4. Check boundary values and critical points.
5. Justify why found extremum is global within constraints.""",
            context=""
        )
        
        computed = await self.programmer(
            instruction="""Implement optimization or sequence calculation:
{analysis}

Compute maximum/minimum or sequence sum. Return precise value for integer conversion.""",
            context=analysis
        )
        
        return await self.revise(
            instruction="Integrate analytical reasoning with computational result. Verify optimality conditions.",
            context=f"{analysis}\n\nCOMPUTATION:\n{computed}"
        )