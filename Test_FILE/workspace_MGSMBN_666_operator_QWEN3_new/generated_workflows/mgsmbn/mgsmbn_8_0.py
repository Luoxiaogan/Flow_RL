# Workflow ID: mgsmbn_8_0
# Benchmark: mgsmbn
# Data Indices: [162]

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

        # PHASE 1: PARALLEL INTERPRETATION — Extract multiple facets simultaneously
        extraction_tasks = [
            self.generate(
                instruction="""Extract all numerical values and their contextual meanings. For each number:
                - What physical quantity does it represent? (e.g., area, rate, count)
                - What are its units? (e.g., একর, টন, ব্যারেল)
                - What entity or action is it associated with?
                Format as bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all agents, objects, and their relationships:
                - Who or what are the main entities? (e.g., Josi, field, grapes, wine)
                - What actions do they perform? (e.g., produces, converts, owns)
                - What are the dependencies or ownerships?
                Present as a structured list with 'Entity: Role → Action' format.""",
                context=""
            ),
            self.generate(
                instruction="""Map the temporal or causal sequence of events:
                - What happens first, second, etc.?
                - Are there conditional or proportional relationships?
                - Highlight any 'hidden steps' not explicitly stated but logically required.
                Use numbered steps with brief explanations.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem type and required operations:
                - Is it sequential, proportional, rate-based, distribution, comparison, or multi-entity?
                - What mathematical operations are needed? (add, multiply, divide, etc.)
                - Are there unit conversions or consistency checks required?
                Provide a classification with justification.""",
                context=""
            )
        ]
        
        extractions = await asyncio.gather(*extraction_tasks)
        
        # Synthesize into unified problem model
        problem_model = await self.ensemble(
            instruction="""Synthesize all extraction facets into a single coherent problem model:
            - Resolve any conflicts between extractions
            - Fill in gaps using logical inference
            - Preserve all numerical values, units, entities, and relationships
            - Explicitly state the target quantity to solve for
            Format as a structured JSON-like outline with sections: 
            [Quantities], [Entities], [Sequence], [Operations], [Target]""",
            contexts_list=extractions
        )

        # PHASE 2: DECOMPOSITION & FORMALIZATION
        subproblems = await self.decompose(
            instruction=f"""Decompose the problem into minimal computational subproblems:
            Using the problem model:
            {problem_model}
            
            Break down into atomic steps where each step:
            - Depends only on previous steps or given values
            - Produces one intermediate result
            - Uses one primary operation (multiply, add, etc.)
            - Tracks units explicitly
            Return as list of subproblems with 'id', 'description', and 'dependencies'.""",
            context=problem_model
        )

        # Solve subproblems in dependency order
        solved_subproblems = {}
        for subproblem in subproblems:
            deps = subproblem.get('dependencies', "").split(",") if subproblem.get('dependencies') else []
            # Wait for dependencies (in real implementation, you'd topologically sort first)
            dep_context = "\n".join([f"{dep_id}: {solved_subproblems.get(dep_id, 'NOT SOLVED')}" 
                                   for dep_id in deps if dep_id.strip()])
            
            sub_context = f"""Problem Model:
{problem_model}

Subproblem to solve:
{subproblem['description']}

Solved Dependencies:
{dep_context}"""

            # Generate and validate code with retries
            solution_attempt = None
            for attempt in range(3):
                try:
                    solution_attempt = await self.programmer(
                        instruction=f"""Generate Python code to solve this subproblem:
                        - Use only given values and solved dependencies
                        - Track units in comments
                        - Output only the numerical result
                        - No print statements, just final value assignment
                        Subproblem: {subproblem['description']}""",
                        context=sub_context,
                        max_retries=1
                    )
                    
                    # Validate result
                    validation = await self.revise(
                        instruction=f"""Critique this solution:
                        - Does the result make sense in context? (Check units, magnitude, logic)
                        - Does it match dependencies and problem constraints?
                        - Is there any arithmetic or unit error?
                        If valid, respond 'VALID'. If not, explain the error concisely.""",
                        context=f"Subproblem: {subproblem['description']}\nSolution: {solution_attempt}"
                    )
                    
                    if "VALID" in validation.upper():
                        break
                    else:
                        sub_context += f"\n\nCRITIQUE (Attempt {attempt+1}): {validation}"
                except Exception as e:
                    sub_context += f"\n\nERROR (Attempt {attempt+1}): {str(e)}"
            
            solved_subproblems[subproblem['id']] = solution_attempt

        # PHASE 3: FINAL SYNTHESIS & VALIDATION
        final_context = f"""Problem Model:
{problem_model}

All Solved Subproblems:
{json.dumps(solved_subproblems, indent=2)}"""

        # Generate final answer
        final_answer_attempt = await self.programmer(
            instruction="""Extract the final numerical answer from the solved subproblems.
            - The answer should be a single number (integer or float)
            - No units, no text, just the number
            - If multiple candidates, choose the one matching the target quantity""",
            context=final_context
        )

        # Run parallel sanity checks
        sanity_checks = await asyncio.gather(
            self.generate(
                instruction="""Unit Consistency Check: 
                Verify that all units cancel appropriately to yield the target unit.
                Trace unit propagation through each subproblem.
                Flag any inconsistencies.""",
                context=final_context
            ),
            self.generate(
                instruction="""Magnitude Plausibility Check:
                Is the final answer reasonable given the problem scale?
                (e.g., 10-acre field shouldn't produce millions of barrels)
                Compare with real-world expectations.""",
                context=final_context
            ),
            self.generate(
                instruction="""Alternative Solution via Dimensional Analysis:
                Solve the entire problem in one step using unit factor method.
                Show the dimensional analysis chain and final result.
                Compare with step-by-step answer.""",
                context=problem_model
            )
        )

        # Ensemble final validation
        final_validation = await self.ensemble(
            instruction="""Synthesize all sanity checks and select final answer:
            - If all checks agree, output the answer
            - If conflicts, resolve by choosing the most consistent with problem constraints
            - Output ONLY the numerical answer, nothing else""",
            contexts_list=[final_answer_attempt] + sanity_checks
        )

        # Extract clean numerical answer
        # Use regex to find first number in the response
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_validation)
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return raw final answer attempt
            match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer_attempt)
            if match:
                return float(match.group()) if '.' in match.group() else int(match.group())
            else:
                return 0  # Ultimate fallback