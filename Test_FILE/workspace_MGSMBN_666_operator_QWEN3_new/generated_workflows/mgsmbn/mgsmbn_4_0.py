# Workflow ID: mgsmbn_4_0
# Benchmark: mgsmbn
# Data Indices: [172]

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

        # STEP 1: PARALLEL PROBLEM FRAMING — Generate 3 interpretations
        framing_instructions = [
            """Analyze this Bengali math problem as a MATHEMATICAL ENTITY MAP:
            - Extract every numerical value and its associated unit (টাকা, ঘণ্টা, জিনিস, etc.)
            - Identify all variables and unknowns
            - Express relationships as equations or pseudo-code
            - Flag any unit conversions needed
            - Do NOT solve yet — only model the structure.
            Output in clear, labeled sections.""",
            
            """Analyze this Bengali math problem as a NARRATIVE CHRONOLOGY:
            - Reconstruct the sequence of events in temporal order
            - For each event, state: (a) what changed, (b) what caused it, (c) what quantity was affected
            - Identify the triggering event and the final goal
            - Highlight any implicit assumptions (e.g., constant rate, no losses)
            Output as a timeline with cause-effect annotations.""",
            
            """Analyze this Bengali math problem via GOAL-ORIENTED BACKWARD CHAINING:
            - Start from the final question being asked
            - What must be known immediately before answering it?
            - Recursively identify prerequisites until reaching given values
            - For each step backward, state the inverse operation needed
            - Identify any missing links or hidden assumptions
            Output as a dependency tree from goal to givens."""
        ]

        framing_results = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in framing_instructions]
        )

        # STEP 2: ENSEMBLE SYNTHESIS — Fuse interpretations into unified structure
        synthesized_structure = await self.ensemble(
            instruction="""Synthesize the three interpretations into ONE coherent problem representation.
            Resolve conflicts by:
            - Preferring interpretations that maintain unit consistency
            - Choosing chronologically plausible sequences
            - Aligning with the explicit goal of the problem
            - Preserving all numerical values and their contexts
            Output a structured summary with:
            1. Known quantities (value + unit)
            2. Unknown target (with expected unit)
            3. Key relationships (as equations or logical dependencies)
            4. Implicit constraints (real-world or mathematical)
            5. Suggested solution path (high-level steps)""",
            contexts_list=framing_results
        )

        # STEP 3: CONDITIONAL DECOMPOSITION — Is decomposition needed?
        decomposition_decision = await self.generate(
            instruction=f"""Analyze this synthesized structure:
            {synthesized_structure}

            DECISION: Does this problem require decomposition into subproblems?
            - If YES: List the minimal set of subproblems with clear dependencies. Each must specify: (a) inputs, (b) operation, (c) output with unit, (d) prerequisite subproblems.
            - If NO: Explain why it can be solved in a single step (e.g., direct formula, single operation).
            Output either the subproblem list OR the justification for atomic solution.""",
            context=synthesized_structure
        )

        # Initialize solution path
        final_computation_context = synthesized_structure
        subproblem_results = []

        if "subproblem" in decomposition_decision.lower() or "ধাপ" in decomposition_decision.lower():
            # STEP 4A: DECOMPOSE AND RESOLVE SUBPROBLEMS
            subproblems = await self.decompose(
                instruction=f"""Decompose this problem into minimal, executable subproblems.
                Rules:
                - Each subproblem must be self-contained with explicit inputs and outputs
                - Track units rigorously — specify input and output units for each
                - Order by dependency: resolve prerequisites first
                - Prefer subproblems that handle unit conversions or intermediate unknowns early
                - Maximum 5 subproblems — if more are needed, group logically
                Use the synthesized structure as your guide: {synthesized_structure}""",
                context=decomposition_decision
            )

            # Resolve subproblems in dependency order
            resolved = {}
            for sp in subproblems:
                # Wait for dependencies
                deps = sp.get('dependencies', "").split(",") if sp.get('dependencies') else []
                for dep_id in deps:
                    dep_id = dep_id.strip()
                    if dep_id and dep_id not in resolved:
                        # In practice, we'd topologically sort — here we assume ordered input
                        pass

                # Generate symbolic solution and code in parallel
                symbolic_attempt = await self.generate(
                    instruction=f"""Solve this subproblem symbolically:
                    {sp['description']}
                    Show all reasoning steps. Track units explicitly. Output final value with unit.""",
                    context=synthesized_structure
                )

                code_attempt = await self.programmer(
                    instruction=f"""Generate Python code to solve this subproblem:
                    {sp['description']}
                    Use only basic arithmetic. Track units in variable names (e.g., total_cost_taka, hours_worked).
                    Output only the numerical result — no explanations.
                    Context: {synthesized_structure}""",
                    context=sp['description']
                )

                # Ensemble to verify
                verified_result = await self.ensemble(
                    instruction="""Compare the symbolic reasoning and code output for this subproblem.
                    - If they agree numerically (within 0.01 tolerance), accept the result.
                    - If they disagree, identify which is more likely correct based on unit handling and step logic.
                    - Output the verified numerical result with unit as: "VALUE UNIT" (e.g., "44 ঘণ্টা")""",
                    contexts_list=[symbolic_attempt, code_attempt]
                )
                
                resolved[sp['id']] = verified_result
                subproblem_results.append(verified_result)

            # Update context with resolved subproblems
            final_computation_context = f"{synthesized_structure}\n\nResolved Subproblems:\n" + "\n".join(subproblem_results)

        # STEP 5: ADVERSARIAL VALIDATION LOOP (up to 2 iterations)
        current_answer = await self.generate(
            instruction=f"""Based on this analysis, compute the final answer:
            {final_computation_context}
            Show your final calculation clearly. Output the numerical result with unit.""",
            context=final_computation_context
        )

        for iteration in range(2):  # Max 2 revisions
            critique = await self.revise(
                instruction=f"""CRITIQUE THIS ANSWER ASSUMING IT IS WRONG:
                Answer: {current_answer}
                
                Attack from three angles:
                1. UNIT CONSISTENCY: Do all steps preserve or convert units correctly? Is the final unit appropriate for the question?
                2. MAGNITUDE SANITY: Is the numerical value absurdly large or small given the context? (e.g., 1000 hours for a part-time job?)
                3. NARRATIVE ALIGNMENT: Does this actually answer what was asked in the original Bengali question?
                
                If any flaw is found, explain precisely how to fix it. If no flaws, output "VERIFIED: NO ISSUES".""",
                context=current_answer
            )

            if "verified" in critique.lower() or "no issues" in critique.lower():
                break
            else:
                current_answer = await self.revise(
                    instruction=f"""REVISE based on this critique:
                    {critique}
                    
                    Re-solve the problem incorporating the feedback. Maintain unit tracking and step clarity.
                    Output the corrected numerical result with unit.""",
                    context=current_answer
                )

        # STEP 6: FINAL ANSWER EXTRACTION
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from this text.
            - Remove all units, explanations, and context
            - Output a single number (integer or decimal) as string
            - If multiple numbers, pick the one that answers the original question
            - Example: if text says "44 ঘণ্টা", output "44" """,
            context=current_answer
        )

        return final_answer.strip()