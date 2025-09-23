# Workflow ID: mgsmbn_87_0
# Benchmark: mgsmbn
# Data Indices: [95, 163]

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

        # PHASE 1: PARALLEL SEMANTIC INTERPRETATION
        # Generate 3 independent interpretations to capture ambiguity
        interpretations = await asyncio.gather(
            self.generate(
                instruction="""Perform deep semantic parsing of the Bengali math problem. Extract:
                1. All named entities (people, objects) with their roles
                2. All numerical values with their units and contextual meaning
                3. Temporal relationships (before/after, duration)
                4. Mathematical relationships (percentages, ratios, comparisons)
                5. The exact unknown being asked for
                Structure output as: ENTITY: [list], VALUE: [list], RELATION: [list], TARGET: [description]""",
                context=""
            ),
            self.generate(
                instruction="""Create mathematical interpretation focusing on operations:
                1. Identify sequence of operations needed (chronological or logical)
                2. Map Bengali phrases to mathematical operators (+, -, ×, ÷, %, etc.)
                3. Note any hidden steps or implicit calculations
                4. Specify units for each quantity and conversion requirements
                5. Highlight potential pitfalls (e.g., percentage of what?)
                Format as: STEPS: [numbered list], OPERATORS: [mapping], UNITS: [specifications], CAUTIONS: [list]""",
                context=""
            ),
            self.generate(
                instruction="""Generate real-world grounded interpretation:
                1. What real-world constraints apply? (e.g., no negative money, integer items)
                2. What would make an answer obviously wrong?
                3. Are there cultural or contextual assumptions?
                4. What sanity checks can be performed?
                5. How would you explain this to a 5th grader?
                Structure as: CONSTRAINTS: [list], SANITY_CHECKS: [list], EXPLANATION: [paragraph]""",
                context=""
            )
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION & EXECUTION
        # Create subproblems from the most structured interpretation (usually index 0)
        decomposition = await self.decompose(
            instruction="""Break down the problem into minimal computational subproblems.
            Each subproblem should be solvable independently if dependencies are met.
            For each subproblem:
            - Specify input variables and their sources
            - Define exact mathematical operation
            - State expected output with units
            - List dependencies (other subproblem IDs)
            Prioritize chronological or causal order.""",
            context=interpretations[0]
        )

        # Execute each subproblem in dependency order
        subproblem_results = {}
        for subproblem in decomposition:
            # Wait for dependencies
            deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            for dep_id in deps:
                dep_id = dep_id.strip()
                if dep_id and dep_id not in subproblem_results:
                    # If dependency not resolved, execute it first (simplified topological sort)
                    dep_sub = next((sp for sp in decomposition if sp['id'] == dep_id), None)
                    if dep_sub:
                        dep_result = await self.programmer(
                            instruction=f"""Solve this subproblem with strict constraints:
                            Problem: {dep_sub['description']}
                            Context from interpretations: {' '.join(interpretations)}
                            Rules:
                            - Use variable names matching entities
                            - Track units throughout
                            - Validate against real-world constraints
                            - Return only final numerical answer
                            - If error, return 'ERROR: [reason]'""",
                            context=dep_sub['description']
                        )
                        subproblem_results[dep_id] = dep_result

            # Execute current subproblem
            result = await self.programmer(
                instruction=f"""Solve this subproblem with strict constraints:
                Problem: {subproblem['description']}
                Context from interpretations: {' '.join(interpretations)}
                Previous results: {subproblem_results}
                Rules:
                - Use variable names matching entities
                - Track units throughout
                - Validate against real-world constraints
                - Return only final numerical answer
                - If error, return 'ERROR: [reason]'""",
                context=subproblem['description']
            )
            subproblem_results[subproblem['id']] = result

        # PHASE 3: VALIDATION & ENSEMBLE
        # Validate each subproblem result against constraints
        validations = await asyncio.gather(*[
            self.generate(
                instruction=f"""Validate this result: {result}
                Against interpretations: {interpretations[2]} (real-world constraints)
                Check:
                1. Does it violate any real-world constraints? (negative, fractional people, etc.)
                2. Does it pass sanity checks?
                3. Is unit correct?
                4. Is magnitude reasonable?
                Return 'VALID' or 'INVALID: [reasons]'""",
                context=result
            ) for result in subproblem_results.values()
        ])

        # If any invalid, trigger revision
        if any("INVALID" in v for v in validations):
            # Summarize validation failures
            failure_summary = await self.summarize(
                instruction="Summarize all validation failures concisely for revision",
                context="\n".join(validations)
            )
            
            # Revise the problematic interpretations
            revised_interpretations = await asyncio.gather(*[
                self.revise(
                    instruction=f"""Revise this interpretation based on validation failures:
                    Failures: {failure_summary}
                    Rules:
                    - Correct mathematical relationships
                    - Enforce real-world constraints
                    - Clarify ambiguous references
                    - Maintain unit consistency""",
                    context=interp
                ) for interp in interpretations
            ])
            
            # Re-execute with revised interpretations
            fallback_results = await asyncio.gather(*[
                self.programmer(
                    instruction=f"""Solve using revised interpretations:
                    Interpretations: {revised_interpretations}
                    Subproblem: {sp['description']}
                    Rules: Strict unit tracking, constraint validation, return only number""",
                    context=sp['description']
                ) for sp in decomposition
            ])
            final_results = fallback_results
        else:
            final_results = list(subproblem_results.values())

        # PHASE 4: FINAL ENSEMBLE & EXTRACTION
        # Extract numerical answer from final results
        answer_candidates = await asyncio.gather(*[
            self.generate(
                instruction="""Extract ONLY the final numerical answer from this text.
                If multiple numbers, identify the one that answers the original question.
                If no clear answer, return 'UNCLEAR'.
                Return ONLY the number or 'UNCLEAR' - no units, no explanation.""",
                context=str(result)
            ) for result in final_results
        ])

        # Ensemble to select best answer
        final_answer = await self.ensemble(
            instruction="""Select the best numerical answer:
            1. Prefer answers that are consistent across multiple sources
            2. Validate against real-world constraints from interpretations
            3. Choose most precise (avoid rounded values unless specified)
            4. If all unclear, return '0' as fallback
            Return ONLY the numerical answer - no explanation.""",
            contexts_list=answer_candidates
        )

        # Clean and return final answer
        # Extract number from text (handle cases where ensemble returns explanation)
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: try to extract from any subproblem result
            for result in final_results:
                match = re.search(r'[-+]?\d*\.\d+|\d+', str(result))
                if match:
                    return float(match.group()) if '.' in match.group() else int(match.group())
            return 0  # Ultimate fallback