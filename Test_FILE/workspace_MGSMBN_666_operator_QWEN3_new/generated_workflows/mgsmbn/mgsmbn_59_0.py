# Workflow ID: mgsmbn_59_0
# Benchmark: mgsmbn
# Data Indices: [160, 103]

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

        # === PHASE 1: PARALLEL MULTI-PERSPECTIVE ANALYSIS ===
        # Generate three independent analyses: mathematical, linguistic, contextual
        math_analysis = await self.generate(
            instruction="""Analyze this Bengali math problem from a purely mathematical perspective:
            - Identify all numerical values and their meanings
            - Determine the mathematical operations required (add, subtract, multiply, divide, etc.)
            - Note any formulas, rates, or proportions involved
            - Ignore linguistic nuances; focus only on quantitative relationships
            - Output in structured bullet points""",
            context=""
        )

        linguistic_analysis = await self.generate(
            instruction="""Analyze this Bengali math problem from a linguistic perspective:
            - Identify key verbs, nouns, and relational phrases
            - Note any ambiguous or culturally specific terms
            - Extract explicit and implicit comparisons (e.g., 'more than', 'less than')
            - Highlight temporal sequences (morning/evening, before/after)
            - Output in structured bullet points""",
            context=""
        )

        contextual_analysis = await self.generate(
            instruction="""Analyze this Bengali math problem from a real-world context perspective:
            - What physical entities are involved? (people, objects, units)
            - What are the real-world constraints? (no negative people, integer items, etc.)
            - What is the expected answer format? (integer, decimal, unit)
            - Are there hidden assumptions or common-sense knowledge needed?
            - Output in structured bullet points""",
            context=""
        )

        # === PHASE 2: SYNTHESIZE INTO ROBUST PROBLEM REPRESENTATION ===
        synthesized_analysis = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified, robust problem representation:
            - Resolve any conflicts between perspectives
            - Combine mathematical requirements with linguistic cues and real-world constraints
            - Create a clear problem classification (e.g., 'additive comparison', 'unit rate', 'proportional distribution')
            - Identify all known values, unknowns, and required operations
            - Output as a structured JSON-like format with keys: problem_type, known_values, unknowns, constraints, required_operations""",
            contexts_list=[math_analysis, linguistic_analysis, contextual_analysis]
        )

        # === PHASE 3: DYNAMIC DECOMPOSITION ===
        decomposition_plan = await self.decompose(
            instruction=f"""Decompose this problem based on the synthesized analysis:
            Synthesized Analysis: {synthesized_analysis}
            
            Break down into atomic, sequentially dependent subproblems:
            - Each subproblem should be solvable independently given its dependencies
            - Include explicit mathematical or extractive instructions
            - Respect real-world constraints (e.g., integer outputs where appropriate)
            - Format each subproblem with clear 'what to compute' and 'how to compute'
            - Dependencies should reference other subproblem IDs if needed""",
            context=synthesized_analysis
        )

        # === PHASE 4: HIERARCHICAL SUBPROBLEM SOLVING ===
        # Group subproblems by dependency level
        solved_subproblems = {}
        
        # Get max dependency depth
        all_deps = [item.get('dependencies', '') for item in decomposition_plan]
        max_depth = 0
        for deps in all_deps:
            if deps:
                depth = len(deps.split(','))
                max_depth = max(max_depth, depth)
        
        # Solve level by level
        for level in range(max_depth + 1):
            # Get subproblems at current level
            current_level_problems = []
            for item in decomposition_plan:
                deps = item.get('dependencies', '').split(',') if item.get('dependencies') else []
                if len(deps) == level:
                    current_level_problems.append(item)
            
            if not current_level_problems:
                continue
                
            # Solve current level in parallel
            async def solve_subproblem(subproblem):
                sub_id = subproblem['id']
                description = subproblem['description']
                
                # Classify subproblem type and route accordingly
                if any(keyword in description.lower() for keyword in ['compute', 'calculate', 'multiply', 'divide', 'add', 'subtract']):
                    # Route to Programmer
                    result = await self.programmer(
                        instruction=f"""Solve this subproblem: {description}
                        Known values from previous steps: {json.dumps(solved_subproblems)}
                        Output ONLY the numerical result, no explanation, no units.
                        If calculation requires previous subproblem results, use the values from solved_subproblems.
                        Ensure real-world constraints are respected (e.g., no negative quantities, integers where appropriate).""",
                        context=json.dumps(solved_subproblems)
                    )
                else:
                    # Route to Generate for extraction or simple reasoning
                    result = await self.generate(
                        instruction=f"""Extract or compute based on problem: {description}
                        Use these previously solved values: {json.dumps(solved_subproblems)}
                        Output ONLY the numerical result or extracted value.
                        Be precise and concise.""",
                        context=json.dumps(solved_subproblems)
                    )
                
                return sub_id, result
            
            # Solve all subproblems at this level in parallel
            results = await asyncio.gather(*[solve_subproblem(sp) for sp in current_level_problems])
            
            # Store results
            for sub_id, result in results:
                solved_subproblems[sub_id] = result.strip()

        # === PHASE 5: FINAL ANSWER COMPUTATION & VALIDATION ===
        # Get the final subproblem (usually the last one or marked as final)
        final_subproblem_id = decomposition_plan[-1]['id'] if decomposition_plan else "unknown"
        final_answer_raw = solved_subproblems.get(final_subproblem_id, "")
        
        # Validate reasonableness
        validation = await self.generate(
            instruction=f"""Validate the reasonableness of this answer: {final_answer_raw}
            Problem context: {self.problem_text}
            Synthesized analysis: {synthesized_analysis}
            Check for:
            - Negative values where impossible (people, items, etc.)
            - Fractional values where integers are required
            - Orders of magnitude that seem implausible
            - Consistency with problem constraints
            If answer is reasonable, output "VALID: [answer]"
            If not, output "INVALID: [suggested correction]" """,
            context=final_answer_raw
        )
        
        if "INVALID" in validation:
            # Extract suggested correction
            final_answer = validation.split("INVALID: ")[-1].strip()
        else:
            final_answer = final_answer_raw

        # === PHASE 6: CLEAN NUMERICAL OUTPUT ===
        # Ensure output is clean numerical value
        clean_answer = await self.programmer(
            instruction=f"""Extract only the numerical value from this text: '{final_answer}'
            Remove any units, explanations, or non-numeric characters.
            If multiple numbers, take the final computed result.
            Output must be a single number (integer or decimal).""",
            context=final_answer
        )

        return clean_answer.strip()