# Workflow ID: mgsmbn_103_0
# Benchmark: mgsmbn
# Data Indices: [124, 168]

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

        # PHASE 1: Narrative Understanding & Entity Extraction
        entity_extraction = await self.generate(
            instruction="""Perform deep semantic extraction from the Bengali word problem. Identify and structure:

1. ENTITIES: All actors (people, animals, objects) with roles. Example: "ডেভ (consumer)", "সিগাল (thief)".
2. QUANTITIES: All numbers with their referents and units. Example: "14 (fries eaten by Dave)", "3 (pigeons)".
3. ACTIONS: Verbs indicating state changes, in chronological order. Example: "ate 14 fries → seagull stole half → pigeons ate 3 each".
4. TEMPORAL MARKERS: Words indicating sequence (পরে, আগে, যখন). Map actions to timeline.
5. TARGET: What is being asked? Extract exact question. Example: "initial number of fries".

Format as JSON-like structure with keys: entities, quantities, actions, timeline, target. Be exhaustive.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on extracted structure:
{entity_extraction}

Propose a FORWARD SIMULATION strategy:
- Start from initial state (unknown) and apply operations step by step.
- Define variables for unknowns.
- Show how final state leads to equation.
- Include unit tracking and validation checks.
- Explain why this approach is suitable.""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Based on extracted structure:
{entity_extraction}

Propose a BACKWARD DERIVATION strategy:
- Start from final known state and reverse operations.
- For each action, define inverse operation (add instead of subtract, multiply instead of divide).
- Show step-by-step reconstruction to initial state.
- Handle fractions/percentages as multiplicative inverses.
- Explain advantages of backward approach here.""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Based on extracted structure:
{entity_extraction}

Propose an ALGEBRAIC MODELING strategy:
- Assign variable x to unknown target.
- Write equation representing entire transformation chain.
- Include all intermediate steps as expressions of x.
- Solve equation symbolically.
- Discuss equation complexity and solvability.""",
                context=entity_extraction
            )
        ]
        
        forward_strat, backward_strat, algebraic_strat = await asyncio.gather(*strategy_tasks)

        # Ensemble: Select Best Strategy
        best_strategy = await self.ensemble(
            instruction="""Evaluate the three proposed strategies:
1. Completeness: Does it account for all actions and entities?
2. Mathematical Soundness: Are operations and inverses correctly defined?
3. Computational Feasibility: Can it be implemented without ambiguity?
4. Error Resistance: Does it include validation or unit checks?
5. Simplicity: Is it the most straightforward path to solution?

Select the single best strategy. Return ONLY the full text of the chosen strategy.""",
            contexts_list=[forward_strat, backward_strat, algebraic_strat]
        )

        # PHASE 3: Code Generation with Dynamic Instruction
        solution_code = await self.programmer(
            instruction=f"""Implement the following mathematical strategy EXACTLY:

{best_strategy}

Additional Requirements:
- Use descriptive variable names reflecting entities (e.g., initial_fries, saras_earnings).
- Include unit comments for every quantity (e.g., # dollars, # fries, # times).
- Validate intermediate results: no negative quantities, fractional people, or unit mismatches.
- If validation fails, raise AssertionError with reason.
- Print ONLY the final numerical answer (no text, no units).
- Use exact fractions or decimals as appropriate — avoid floating point if fractions are cleaner.""",
            context=best_strategy
        )

        # PHASE 4: Validation & Self-Correction Loop
        for attempt in range(2):  # Max 2 correction attempts
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
Solution Code Output: {solution_code}

Check:
1. Does the answer make sense in context? (e.g., 48 fries when Dave ate 14 is plausible)
2. Do intermediate steps align with problem narrative? Reconstruct the story with this answer.
3. Are units consistent throughout? (e.g., dollars not mixed with hours)
4. Are there hidden constraints violated? (e.g., fractional children, negative items)

If valid, return "VALID: [reason]". If invalid, return "INVALID: [specific error and suggested fix]\"""",
                context=solution_code
            )

            if "VALID" in validation:
                break
            else:
                # Revise strategy based on validation feedback
                best_strategy = await self.revise(
                    instruction=f"""Revise the mathematical strategy based on this validation feedback:
{validation}

Specifically:
- Correct any misinterpreted operations or sequences.
- Adjust for unit inconsistencies or constraint violations.
- Consider switching to an alternative approach if fundamental flaw exists.
- Maintain clear step-by-step reasoning.

Return the full revised strategy.""",
                    context=best_strategy
                )
                
                # Regenerate code with revised strategy
                solution_code = await self.programmer(
                    instruction=f"""Implement the REVISED mathematical strategy:

{best_strategy}

Same requirements as before: unit tracking, validation, exact output.""",
                    context=best_strategy
                )

        # Extract final numerical answer from code output
        # Programmer output format: "Code: ...\nOutput: <number>"
        lines = solution_code.strip().split('\n')
        answer_line = [line for line in lines if line and not line.startswith('Code:')][-1]
        final_answer = re.sub(r'[^\d.-]', '', answer_line)  # Extract only number

        return final_answer