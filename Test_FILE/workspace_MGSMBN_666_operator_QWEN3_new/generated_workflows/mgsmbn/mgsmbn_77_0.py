# Workflow ID: mgsmbn_77_0
# Benchmark: mgsmbn
# Data Indices: [87]

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

        # PHASE 1: PARALLEL INTERPRETATION (FORK)
        # Generate three complementary lenses: linguistic, mathematical, constraint-aware
        linguistic_parse, math_structure, constraint_model = await asyncio.gather(
            self.generate(
                instruction="""Perform deep linguistic parsing of the Bengali word problem:
                - Identify all named entities (people, objects, places)
                - Extract all numerical values and their referents (what do they quantify?)
                - Map action verbs and their temporal/causal relationships
                - Resolve pronouns and ambiguous references
                - Output as structured JSON with keys: entities, quantities, actions, references""",
                context=""
            ),
            self.generate(
                instruction="""Construct mathematical model from the problem:
                - Identify known values and unknowns
                - Determine relationships between quantities (additive, multiplicative, proportional)
                - Infer implicit operations or hidden steps
                - Map sequence of calculations needed
                - Flag any unit conversions required
                - Output as structured JSON with keys: knowns, unknowns, relationships, operations, units""",
                context=""
            ),
            self.generate(
                instruction="""Identify real-world constraints and boundary conditions:
                - What physical/logical limitations apply? (e.g., no negative quantities, integer-only answers)
                - What contextual assumptions are implied? (e.g., 'sharing equally' implies division)
                - What are reasonable bounds for the answer? (e.g., if counting people, answer > 0)
                - Flag any ambiguities or underspecified conditions
                - Output as structured JSON with keys: constraints, assumptions, bounds, ambiguities""",
                context=""
            )
        )

        # PHASE 2: INDIVIDUAL REFINEMENT
        # Deepen each interpretation with focused revision
        refined_linguistic, refined_math, refined_constraints = await asyncio.gather(
            self.revise(
                instruction="""Enhance linguistic parse with deeper semantic analysis:
                - Disambiguate any remaining vague references
                - Clarify temporal sequence of actions
                - Resolve any pronoun chains or implicit subjects
                - Ensure all quantities are correctly linked to their entities
                - Maintain JSON structure but add depth to each field""",
                context=linguistic_parse
            ),
            self.revise(
                instruction="""Strengthen mathematical model with explicit dependencies:
                - Formalize relationships as equations or expressions
                - Specify order of operations with dependencies
                - Add any missing intermediate steps
                - Explicitly state unit handling strategy
                - Maintain JSON structure but add computational rigor""",
                context=math_structure
            ),
            self.revise(
                instruction="""Sharpen constraint model with domain-specific reasoning:
                - Convert implicit assumptions into explicit rules
                - Quantify reasonable bounds (min/max values)
                - Resolve ambiguities by applying most plausible interpretation
                - Add validation criteria for final answer
                - Maintain JSON structure but add precision to each constraint""",
                context=constraint_model
            )
        )

        # PHASE 3: SYNTHESIZE UNIFIED REPRESENTATION (MERGE)
        unified_model = await self.ensemble(
            instruction="""Synthesize the three refined interpretations into a single coherent problem representation:
            - Reconcile any conflicts between linguistic, mathematical, and constraint views
            - Fill any remaining gaps in the problem model
            - Produce a master JSON structure with:
                * entities: consolidated list with attributes
                * quantities: with units and relationships
                * operations: ordered sequence with dependencies
                * constraints: explicit rules and bounds
                * uncertainties: any remaining ambiguities with confidence levels
            - Prioritize mathematical rigor but respect linguistic and real-world constraints""",
            contexts_list=[refined_linguistic, refined_math, refined_constraints]
        )

        # PHASE 4: DECOMPOSE INTO EXECUTABLE SUBPROBLEMS
        subproblems = await self.decompose(
            instruction="""Break down the unified problem model into executable computational subproblems:
            - Each subproblem should be independently solvable with clear inputs and outputs
            - Specify dependencies between subproblems (which must be solved first)
            - Include necessary unit conversions or intermediate calculations
            - Format each subproblem as: {id, description, dependencies, expected_output_format}
            - Ensure the sequence leads logically to the final answer""",
            context=unified_model
        )

        # PHASE 5: PARALLEL EXECUTION WITH VALIDATION LOOPS
        async def solve_and_validate(subproblem):
            # Initial solution attempt
            solution = await self.programmer(
                instruction=f"""Solve this subproblem using precise computation:
                Subproblem: {subproblem['description']}
                Expected output format: {subproblem.get('expected_output_format', 'numerical value')}
                Show all steps and maintain unit consistency.
                Return only the final numerical result.""",
                context=unified_model
            )
            
            # Validate against constraints
            validation = await self.generate(
                instruction=f"""Validate this subproblem result against real-world constraints:
                Subproblem: {subproblem['description']}
                Result: {solution}
                Constraints from unified model: {unified_model}
                Check for: unit consistency, boundary violations, logical coherence.
                Return 'VALID' if acceptable, or specific error message if not.""",
                context=solution
            )
            
            # If invalid, revise and retry (max 2 retries)
            attempts = 1
            while "VALID" not in validation.upper() and attempts < 3:
                solution = await self.revise(
                    instruction=f"""Revise solution based on validation feedback:
                    Original subproblem: {subproblem['description']}
                    Previous solution: {solution}
                    Validation feedback: {validation}
                    Correct errors and maintain computational precision.""",
                    context=solution
                )
                validation = await self.generate(
                    instruction=f"""Re-validate revised solution:
                    Subproblem: {subproblem['description']}
                    Revised result: {solution}
                    Constraints: {unified_model}
                    Return 'VALID' if acceptable, or specific error message if not.""",
                    context=solution
                )
                attempts += 1
            
            return {
                'subproblem_id': subproblem['id'],
                'solution': solution,
                'validation_status': 'VALID' if 'VALID' in validation.upper() else 'UNCERTAIN',
                'attempts': attempts
            }

        # Execute all subproblems in parallel
        subproblem_results = await asyncio.gather(
            *[solve_and_validate(sp) for sp in subproblems]
        )

        # PHASE 6: FINAL SYNTHESIS AND META-REFLECTION
        final_synthesis = await self.ensemble(
            instruction="""Synthesize subproblem results into final answer:
            - Combine results according to dependency order
            - Perform any final calculations needed
            - Ensure unit consistency in final answer
            - Return ONLY the numerical answer as a string (no units, no explanation)""",
            contexts_list=[json.dumps(r) for r in subproblem_results]
        )

        # Meta-reflection for uncertainty handling
        reflection = await self.generate(
            instruction=f"""Perform meta-reflection on the solution process:
            - Were there any high-uncertainty decisions? (confidence < 80%)
            - Could alternative interpretations yield different answers?
            - Is the final answer consistent with all constraints and bounds?
            - If high uncertainty detected, suggest alternative approaches.
            Return 'CONFIDENT' if solution is robust, or detailed uncertainty analysis if not.""",
            context=f"Final Answer: {final_synthesis}\nSubproblem Results: {json.dumps(subproblem_results)}\nUnified Model: {unified_model}"
        )

        # Fallback for high uncertainty
        if "CONFIDENT" not in reflection.upper():
            # Generate alternative solutions
            alt_approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate alternative solution assuming different interpretation of ambiguous elements:
                    Original problem: {self.problem_text}
                    Current solution: {final_synthesis}
                    Reflection: {reflection}
                    Return only numerical answer.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate conservative solution using most constrained interpretation:
                    Original problem: {self.problem_text}
                    Current solution: {final_synthesis}
                    Reflection: {reflection}
                    Return only numerical answer.""",
                    context=""
                )
            )
            
            # Ensemble with bias toward constrained interpretation
            final_synthesis = await self.ensemble(
                instruction="""Select best answer from alternatives:
                - Prioritize solutions that satisfy the most constraints
                - Prefer interpretations that minimize assumptions
                - Choose the most contextually grounded answer
                Return ONLY the selected numerical answer.""",
                contexts_list=[final_synthesis] + alt_approaches
            )

        return final_synthesis.strip()