# Workflow ID: limr_79_0
# Benchmark: limr
# Data Indices: [149, 191]

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

        # STEP 1: META-CLASSIFICATION & STRATEGIC DECOMPOSITION
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic decomposition:
            1. Identify the primary mathematical domain (combinatorics, number theory, algebra, geometry, probability, etc.)
            2. Detect secondary domains that may be relevant
            3. List all explicit and implicit constraints
            4. Identify what form the answer must take (integer 000-999, fraction, etc.)
            5. Propose 3 distinct high-level solution strategies that could apply
            6. For each strategy, list its core insight and potential pitfalls
            Format as structured markdown with clear section headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Decompose this problem into atomic, solvable subproblems:
            - Each subproblem should be self-contained with clear inputs and expected outputs
            - Identify mathematical domain for each subproblem
            - Specify dependencies between subproblems
            - Flag any subproblem that requires computational verification
            - Flag any subproblem that requires proof or logical derivation
            Return as list of dictionaries with 'id', 'description', 'dependencies', 'domain', 'requires_computation'""",
            context=classification
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION (DIAMOND PATTERN)
        strategy_instructions = [
            """Adopt an ALGEBRAIC/ANALYTICAL lens:
            - Model the problem using equations, functions, or algebraic structures
            - Look for symmetries, invariants, or transformations
            - Express unknowns as variables and derive relationships
            - Avoid combinatorial enumeration unless absolutely necessary
            - Show all derivation steps with justifications""",
            
            """Adopt a COMBINATORIAL/PROBABILISTIC lens:
            - Model as counting problem, probability space, or state transitions
            - Use principles of inclusion-exclusion, recursion, or generating functions
            - Consider complementary counting or symmetry arguments
            - Calculate probabilities as fractions and simplify exactly
            - Avoid algebraic manipulation unless it simplifies counting""",
            
            """Adopt a NUMBER THEORETIC/STRUCTURAL lens:
            - Look for patterns in modular arithmetic, divisibility, or prime structure
            - Consider Diophantine constraints or extremal principles
            - Use mathematical induction or proof by contradiction if applicable
            - Focus on structural properties rather than numerical computation
            - Derive general form before plugging in specific values"""
        ]

        strategy_branches = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: ADVERSARIAL REVISION & INSIGHT DISTILLATION
        revised_branches = []
        for i, branch in enumerate(strategy_branches):
            # First revision: improve clarity and fill gaps
            improved = await self.revise(
                instruction=f"""Improve this solution attempt:
                - Fill any logical gaps or missing steps
                - Add explicit justifications for non-obvious claims
                - Verify that all constraints from classification are addressed
                - If computation is needed, outline exactly what needs to be calculated
                - Preserve the core strategy but strengthen its rigor""",
                context=branch
            )
            # Second revision: adversarial validation
            validated = await self.revise(
                instruction="""Adopt an adversarial stance:
                - Assume this solution contains a critical error
                - Systematically check each step for logical flaws, calculation errors, or violated assumptions
                - If you find an error, correct it; if not, strengthen the weakest argument
                - Output the corrected version with a brief summary of what you validated""",
                context=improved
            )
            # Summarize key insights for synthesis
            distilled = await self.summarize(
                instruction="""Extract and structure the core insights:
                Format as:
                CORE_INSIGHT: [one sentence]
                KEY_EQUATION/PRINCIPLE: [mathematical statement]
                VERIFIED_ASSUMPTIONS: [list]
                UNRESOLVED_QUESTIONS: [list or 'None']
                FINAL_ANSWER_CANDIDATE: [integer or expression]""",
                context=validated
            )
            revised_branches.append(distilled)

        # STEP 4: SYNTHESIS & CONSENSUS BUILDING
        synthesis = await self.ensemble(
            instruction="""Synthesize the three solution branches into a unified answer:
            - Compare core insights and identify complementary approaches
            - Resolve conflicts by tracing back to original problem constraints
            - If branches agree, select the most rigorously justified answer
            - If branches disagree, create a hybrid solution that combines their strongest elements
            - Output must include: 1) Final answer as integer 000-999, 2) Brief justification, 3) Confidence level (High/Medium/Low)""",
            contexts_list=revised_branches
        )

        # STEP 5: CONFIDENCE-DRIVEN ITERATIVE REFINEMENT
        confidence = await self.generate(
            instruction="""Assess confidence in the synthesized solution:
            - Is the answer mathematically rigorous?
            - Are all edge cases handled?
            - Is the integer answer within 000-999?
            - Are there any remaining logical gaps?
            Output 'High', 'Medium', or 'Low' followed by brief justification""",
            context=synthesis
        )

        final_answer = synthesis
        if "low" in confidence.lower() or "medium" in confidence.lower():
            # Trigger adaptive refinement
            refinement = await self.generate(
                instruction=f"""Given confidence assessment: {confidence}
                And previous synthesis: {synthesis}
                Generate a NEW solution strategy that:
                - Avoids the weaknesses identified in previous attempts
                - Explores a fundamentally different mathematical perspective
                - Focuses on the most uncertain subproblems identified in decomposition
                - Must produce an integer answer between 000-999
                Show complete derivation with verification steps""",
                context=f"{classification}\n\n{decomposition}"
            )
            
            # Final adversarial validation
            final_answer = await self.revise(
                instruction="""Final verification pass:
                - Assume this is your last chance to get the correct answer
                - Check every calculation and logical step with extreme skepticism
                - Verify answer is integer between 000-999
                - If answer is fractional or out of range, trace back and correct
                - Output ONLY the final integer answer in format: ###ANSWER: XXX###""",
                context=refinement
            )
        else:
            # High confidence path: format and verify
            final_answer = await self.revise(
                instruction="""Final formatting and verification:
                - Extract the integer answer from synthesis
                - Verify it is between 000-999
                - If not, correct the calculation
                - Output ONLY in format: ###ANSWER: XXX###""",
                context=synthesis
            )

        # STEP 6: ANSWER EXTRACTION & VALIDATION
        # Extract answer using regex to ensure format compliance
        match = re.search(r"###ANSWER:\s*(\d{3})###", final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any 3-digit number as last resort
            numbers = re.findall(r"\b\d{3}\b", final_answer)
            if numbers:
                return numbers[0]
            else:
                # Ultimate fallback: return 000 (should never happen in well-designed workflow)
                return "000"