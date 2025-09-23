# Workflow ID: mgsmbn_70_0
# Benchmark: mgsmbn
# Data Indices: [43, 173]

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
        
        # Step 1: Parallel classification and initial decomposition
        classification_task = self.generate(
            instruction="""Classify this Bengali math word problem with extreme precision:
            1. Identify the PRIMARY problem type: Sequential, Rate, Proportional, Distribution, or Comparison.
            2. List all NUMERICAL VALUES with their semantic roles (e.g., 'base_amount', 'percentage', 'fixed_fee', 'time', 'rate').
            3. Extract all OPERATIONAL VERBS and their implied mathematical operations (e.g., 'যোগ' → addition, 'কম' → subtraction).
            4. Flag any AMBIGUITIES, unit mismatches, or real-world implausibilities.
            5. Predict the expected answer format (integer, decimal, currency, etc.).
            Output in structured JSON-like format for machine parsing.""",
            context=""
        )
        
        decomposition_task = self.decompose(
            instruction="""Decompose this problem into minimal, ordered, executable subproblems:
            - Each subproblem must be solvable independently given its dependencies.
            - Explicitly state dependencies using subproblem IDs.
            - Map each subproblem to a precise mathematical operation.
            - Include unit tracking and conversion requirements.
            - Handle implicit steps (e.g., '25% fee' implies multiplication then addition).
            - Output must be machine-readable list of dicts with 'id', 'description', 'dependencies'.""",
            context=""
        )
        
        # Execute in parallel
        classification, decomposition = await asyncio.gather(classification_task, decomposition_task)
        
        # Step 2: Validate and refine decomposition
        validated_decomposition = await self.revise(
            instruction=f"""Critically validate the decomposition against the problem classification:
            Classification: {classification}
            
            Validation Criteria:
            1. Does each subproblem align with the identified problem type?
            2. Are all numerical entities from classification accounted for?
            3. Are dependencies correctly ordered (especially for sequential operations)?
            4. Are units consistently tracked?
            5. Are edge cases (fractions, negatives, zero) handled?
            
            Revise the decomposition list to fix any gaps, reorder if needed, and add missing validation steps.
            Maintain strict machine-readable format.""",
            context=str(decomposition)
        )
        
        # Step 3: Topological sort of subproblems (resolve dependencies)
        # Convert string back to list of dicts (assuming valid JSON-like structure)
        import ast
        try:
            subproblems = ast.literal_eval(validated_decomposition)
        except:
            # Fallback: use original decomposition if parsing fails
            subproblems = ast.literal_eval(str(decomposition))
        
        # Build dependency graph and sort
        from collections import defaultdict, deque
        graph = defaultdict(list)
        indegree = defaultdict(int)
        id_to_subproblem = {sp['id']: sp for sp in subproblems}
        
        for sp in subproblems:
            deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
            for dep in deps:
                dep = dep.strip()
                if dep:
                    graph[dep].append(sp['id'])
                    indegree[sp['id']] += 1
        
        # Topological sort
        queue = deque([sp['id'] for sp in subproblems if indegree[sp['id']] == 0])
        sorted_ids = []
        while queue:
            node = queue.popleft()
            sorted_ids.append(node)
            for neighbor in graph[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Step 4: Solve subproblems in order, with context accumulation
        solution_context = {}
        for sp_id in sorted_ids:
            sp = id_to_subproblem[sp_id]
            
            # Build context from dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {solution_context.get(dep, 'Not solved yet')}" 
                                   for dep in sp.get('dependencies', '').split(',') if dep.strip()])
            
            # Generate code for this subproblem
            code_result = await self.programmer(
                instruction=f"""Solve this subproblem with extreme precision:
                Subproblem: {sp['description']}
                Dependencies: {dep_context}
                
                Requirements:
                - Write minimal, correct Python code.
                - Use ONLY the values and operations specified.
                - Track units if mentioned.
                - Output ONLY the numerical result (no text, no units).
                - Handle edge cases (division by zero, negative results if invalid).
                - If ambiguous, choose the most mathematically conventional interpretation.""",
                context=dep_context
            )
            
            # Extract numerical result from code output
            numerical_result = await self.summarize(
                instruction="""Extract ONLY the final numerical answer from the code output.
                Remove all text, units, explanations. If multiple numbers, pick the final result.
                If no number found, return 'ERROR'. Output must be parseable as float or int.""",
                context=code_result
            )
            
            solution_context[sp_id] = numerical_result.strip()
        
        # Step 5: Parallel validation of final result
        final_answer = solution_context.get(sorted_ids[-1], "ERROR") if sorted_ids else "ERROR"
        
        validators = await asyncio.gather(
            self.generate(
                instruction=f"""UNIT VALIDATION: 
                Original problem: {self.problem_text}
                Final answer: {final_answer}
                Check: Do units make sense? (e.g., no fractional people, positive quantities, currency format).
                Output 'VALID' or 'INVALID' with brief reason.""",
                context=final_answer
            ),
            self.generate(
                instruction=f"""PLAUSIBILITY CHECK:
                Does {final_answer} make real-world sense given the problem context?
                Example: Grocery bill shouldn't be $0.01 or $1000000 for normal items.
                Output 'PLAUSIBLE' or 'IMPLAUSIBLE' with reason.""",
                context=final_answer
            ),
            self.generate(
                instruction=f"""REVERSE ENGINEERING:
                Starting from answer {final_answer}, can you reconstruct the problem's narrative?
                If yes, output 'CONSISTENT'. If not, output 'INCONSISTENT' with gap description.""",
                context=final_answer
            )
        )
        
        # Step 6: Ensemble final decision with fallback
        final_decision = await self.ensemble(
            instruction=f"""Synthesize validation results to produce final answer:
            Validators: {validators}
            Original answer: {final_answer}
            
            Decision Rules:
            1. If all validators pass → return original answer.
            2. If any validator fails → trigger revision with specific feedback.
            3. If revision fails → return original answer with warning (but we must return a number).
            
            Output ONLY the final numerical answer, nothing else.""",
            contexts_list=[final_answer] + list(validators)
        )
        
        # Step 7: Final formatting (ensure pure number)
        clean_answer = await self.summarize(
            instruction="""Extract ONLY the numerical value from the text.
            Remove all non-numeric characters except decimal point.
            If integer, output without decimal. If decimal, preserve precision.
            Example: '$57.00' → '57', '57.5 kg' → '57.5', 'ERROR' → '0' (fallback).""",
            context=final_decision
        )
        
        return clean_answer.strip()