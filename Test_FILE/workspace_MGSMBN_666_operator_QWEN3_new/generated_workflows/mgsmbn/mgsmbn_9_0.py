# Workflow ID: mgsmbn_9_0
# Benchmark: mgsmbn
# Data Indices: [82, 138]

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

        # Step 1: Semantic Filtering - Classify sentences and extract core constraints
        semantic_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of the Bengali problem:
            - Classify each sentence as: [NUMERICAL CONSTRAINT], [CONTEXTUAL FLAVOR], [IMPLICIT ASSUMPTION], or [QUESTION TARGET]
            - Extract all explicit numerical values with their semantic roles (e.g., "3 miles" → distance_rate_basis)
            - Identify all mathematical relationships (ratios, averages, proportions, dependencies)
            - Flag any ambiguous phrases that might have multiple interpretations
            - Output in structured JSON format with keys: classifications, values, relationships, ambiguities""",
            context=""
        )

        # Step 2: Hierarchical Decomposition with Dependency Mapping
        subproblems = await self.decompose(
            instruction=f"""Decompose the problem into minimal solvable subproblems using this strategy:
            1. Use semantic analysis to ignore [CONTEXTUAL FLAVOR] sentences
            2. Each subproblem must correspond to one mathematical relationship or direct computation
            3. Express dependencies: if subproblem B requires result from subproblem A, list A in dependencies
            4. For algebraic relationships, create subproblem to "solve for X" where X is unknown
            5. For proportional relationships, create subproblem to "set up and solve proportion"
            6. Final subproblem must combine all results to answer the ultimate question
            Semantic context: {semantic_analysis}""",
            context=""
        )

        # Step 3: Parallel Classification of Subproblem Types
        classification_tasks = []
        for sp in subproblems:
            task = self.generate(
                instruction=f"""Classify this subproblem for optimal solving strategy:
                Subproblem: {sp['description']}
                Choose exactly one type: [DIRECT_COMPUTATION], [ALGEBRAIC_DERIVATION], [PROPORTIONAL_SCALING], [UNIT_CONVERSION]
                Also estimate complexity: [SIMPLE], [MODERATE], [COMPLEX]
                Output format: TYPE|COMPLEXITY""",
                context=""
            )
            classification_tasks.append(task)
        
        classifications = await asyncio.gather(*classification_tasks)

        # Step 4: Build Execution Plan with Conditional Routing
        solution_context = {}
        subproblem_results = {}
        
        # Process subproblems in dependency order
        for sp in subproblems:
            sp_id = sp['id']
            description = sp['description']
            deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
            
            # Wait for dependencies
            dep_context = "\n".join([f"{dep_id}: {subproblem_results[dep_id]}" for dep_id in deps if dep_id in subproblem_results])
            
            # Get classification
            sp_class = classifications[int(sp_id.split('_')[-1]) - 1] if sp_id.split('_')[-1].isdigit() else classifications[0]
            sp_type = sp_class.split('|')[0] if '|' in sp_class else "DIRECT_COMPUTATION"
            
            # Route to appropriate solver with context-aware instructions
            if sp_type == "ALGEBRAIC_DERIVATION":
                # Generate symbolic equation first
                equation_draft = await self.generate(
                    instruction=f"""Convert this algebraic subproblem into formal mathematical equation:
                    Subproblem: {description}
                    Available values: {dep_context}
                    Semantic context: {semantic_analysis}
                    Output ONLY the equation in standard mathematical notation (e.g., 'x + 2y = 10')""",
                    context=dep_context
                )
                
                # Solve with programmer
                result = await self.programmer(
                    instruction=f"""Solve this algebraic equation for the unknown variable:
                    Equation: {equation_draft}
                    Show all steps and verify solution.
                    If multiple solutions, choose the one that makes physical sense (positive, non-fractional for countable items).""",
                    context=equation_draft
                )
                
            elif sp_type == "PROPORTIONAL_SCALING":
                proportion_setup = await self.generate(
                    instruction=f"""Set up proportion for this scaling problem:
                    Subproblem: {description}
                    Known ratio: extract from semantic analysis
                    Target value: what we're solving for
                    Format: 'known_ratio = target_ratio' (e.g., '3/10 = 42/x')""",
                    context=dep_context
                )
                
                result = await self.programmer(
                    instruction=f"""Solve this proportion for the unknown:
                    Proportion: {proportion_setup}
                    Cross-multiply and solve step by step.
                    Verify answer makes sense in context.""",
                    context=proportion_setup
                )
                
            else:  # DIRECT_COMPUTATION or UNIT_CONVERSION
                result = await self.programmer(
                    instruction=f"""Perform direct computation for this subproblem:
                    Subproblem: {description}
                    Available values: {dep_context}
                    Semantic context: {semantic_analysis}
                    Write explicit formula, then compute.
                    Track units throughout and convert if necessary.""",
                    context=dep_context
                )
            
            # Validate result contextually
            validation = await self.generate(
                instruction=f"""Validate this result for real-world plausibility:
                Subproblem: {description}
                Result: {result}
                Check for: negative values (invalid for counts/distances), fractional people/objects (unless specified), 
                unit mismatches, values that contradict problem constraints.
                If valid, output 'VALID: [result]'. If invalid, output 'INVALID: [reason]'""",
                context=result
            )
            
            # If invalid, try ensemble reinterpretation
            if "INVALID" in validation:
                # Generate 3 alternative interpretations
                alternatives = await asyncio.gather(
                    self.generate(instruction=f"Reinterpret subproblem literally: {description}", context=dep_context),
                    self.generate(instruction=f"Reinterpret subproblem with implicit rounding: {description}", context=dep_context),
                    self.generate(instruction=f"Reinterpret subproblem by rephrasing Bengali: {description}", context=dep_context)
                )
                
                # Solve each alternative
                alt_solutions = []
                for alt in alternatives:
                    alt_solution = await self.programmer(
                        instruction=f"Solve this reinterpretation: {alt}\nUse available context: {dep_context}",
                        context=alt
                    )
                    alt_solutions.append(alt_solution)
                
                # Ensemble select best
                result = await self.ensemble(
                    instruction=f"""Select the most plausible solution for subproblem: {description}
                    Consider: mathematical correctness, contextual plausibility, unit consistency.
                    Solutions to evaluate: {alt_solutions}""",
                    contexts_list=alt_solutions
                )
            
            # Store result
            subproblem_results[sp_id] = result
            solution_context[sp_id] = result

        # Step 5: Final Synthesis and Cross-Validation
        final_answer_draft = await self.generate(
            instruction=f"""Synthesize final answer from all subproblem results:
            Subproblem results: {json.dumps(subproblem_results, indent=2)}
            Ultimate question: extract from original problem
            Write explicit formula combining all results to answer the question.
            Example: 'total_cost = hat_price + jacket_price + pants_price'""",
            context=json.dumps(subproblem_results)
        )
        
        final_answer = await self.programmer(
            instruction=f"""Compute final answer using this synthesis:
            Synthesis formula: {final_answer_draft}
            All subproblem results: {json.dumps(subproblem_results)}
            Execute calculation and output ONLY the numerical result.""",
            context=final_answer_draft
        )
        
        # Final validation
        final_validation = await self.generate(
            instruction=f"""Final validation of answer:
            Answer: {final_answer}
            Does this match the problem's expected format (single numerical value)?
            Is it within reasonable bounds for the context?
            If yes, output exactly: 'FINAL_ANSWER: [number]'
            If no, output: 'REJECTED: [reason]' and suggest correction.""",
            context=final_answer
        )
        
        if "FINAL_ANSWER:" in final_validation:
            final_result = final_validation.split("FINAL_ANSWER:")[1].strip()
        else:
            # Fallback: return raw computation if validation fails
            final_result = final_answer.strip()

        return final_result