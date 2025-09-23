# Workflow ID: mgsmbn_45_0
# Benchmark: mgsmbn
# Data Indices: [133, 60]

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

        # STEP 1: INITIAL ANALYSIS - CLASSIFY PROBLEM & EXTRACT STRUCTURE
        problem_analysis = await self.generate(
            instruction="""
            Perform deep structural analysis of this Bengali math word problem:
            
            1. CLASSIFY the problem type:
               - Sequential operations (deposit/withdrawal, multi-step chronology)
               - Rate problems (speed/time, unit price, work rate)
               - Proportional reasoning (percentages, fractions, ratios, scaling)
               - Distribution (sharing, division with remainders)
               - Comparison (differences, "how many more")
               - Multi-entity tracking (multiple people/objects with different values)
            
            2. EXTRACT all entities and quantities:
               - List every named person/object and their associated quantities
               - Extract all numbers with their units (টাকা, ঘণ্টা, জিনিস, etc.)
               - Identify what is being asked (the unknown)
            
            3. IDENTIFY mathematical relationships:
               - What operations connect the quantities? (+, -, ×, ÷, %, etc.)
               - Are there hidden steps or implicit calculations?
               - Note any constraints (non-negative, whole numbers, unit conversions)
            
            4. OUTPUT FORMAT:
               Structure your response as:
               Problem Type: [type]
               Entities: [list with quantities and units]
               Unknown: [what we're solving for]
               Operations: [sequence of mathematical steps needed]
               Constraints: [any real-world or mathematical limitations]
            """,
            context=""
        )

        # STEP 2: CONDITIONAL DECOMPOSITION - ONLY IF COMPLEX
        if any(keyword in problem_analysis.lower() for keyword in ["sequential", "multi-step", "multiple", "dependent"]):
            decomposition = await self.decompose(
                instruction=f"""
                Based on this problem analysis:
                {problem_analysis}
                
                Decompose the problem into minimal, solvable subproblems. For each subproblem:
                - Clearly state what needs to be calculated
                - Specify input values and their sources (original problem or other subproblems)
                - Note required operations and expected output format
                - Include unit tracking requirements
                - Mark dependencies explicitly (which subproblems must be solved first)
                
                Ensure subproblems are granular enough for direct computation but not overly fragmented.
                """,
                context=problem_analysis
            )
            
            # STEP 3A: SOLVE SUBPROBLEMS IN PARALLEL WHERE POSSIBLE
            subproblem_solutions = {}
            dependency_graph = {sp['id']: sp['dependencies'].split(',') if sp['dependencies'] else [] for sp in decomposition}
            
            # Solve in topological order
            solved_ids = set()
            while len(solved_ids) < len(decomposition):
                # Find subproblems with all dependencies resolved
                ready_subproblems = [
                    sp for sp in decomposition 
                    if sp['id'] not in solved_ids and all(dep.strip() in solved_ids for dep in dependency_graph[sp['id']])
                ]
                
                if not ready_subproblems:
                    break  # Circular dependency or error
                
                # Solve ready subproblems in parallel
                solve_tasks = []
                for sp in ready_subproblems:
                    context_for_sp = f"Problem Analysis: {problem_analysis}\nSubproblem: {sp['description']}\nSolved so far: {json.dumps(subproblem_solutions)}"
                    solve_task = self.programmer(
                        instruction=f"""
                        Solve this mathematical subproblem:
                        {sp['description']}
                        
                        Context from problem analysis:
                        {problem_analysis}
                        
                        Previously solved subproblems:
                        {json.dumps(subproblem_solutions)}
                        
                        Requirements:
                        - Show all calculation steps
                        - Track units throughout (টাকা, ঘণ্টা, etc.)
                        - Round appropriately (currency to 2 decimals, people to whole numbers)
                        - Validate against constraints (no negative quantities, etc.)
                        - Output ONLY the final numerical result with unit if applicable
                        """,
                        context=context_for_sp
                    )
                    solve_tasks.append((sp['id'], solve_task))
                
                # Execute parallel tasks
                results = await asyncio.gather(*[task for _, task in solve_tasks])
                for (sp_id, _), result in zip(solve_tasks, results):
                    subproblem_solutions[sp_id] = result
                    solved_ids.add(sp_id)
            
            # Final answer should be in the last solved subproblem (or specified in decomposition)
            candidate_answer = list(subproblem_solutions.values())[-1] if subproblem_solutions else "0"
            
        else:
            # STEP 3B: DIRECT SOLUTION FOR SIMPLE PROBLEMS
            candidate_answer = await self.programmer(
                instruction=f"""
                Solve this Bengali math problem directly:
                
                Problem Analysis:
                {problem_analysis}
                
                Requirements:
                - Extract all relevant numbers and operations
                - Perform calculations in correct order
                - Track units throughout (টাকা, ঘণ্টা, etc.)
                - Apply real-world constraints (no negative money, whole people, etc.)
                - Round appropriately (currency to 2 decimals)
                - Output ONLY the final numerical answer
                """,
                context=problem_analysis
            )

        # STEP 4: GENERATE ALTERNATIVE SOLUTION PATH FOR VALIDATION
        alternative_solution = await self.programmer(
            instruction=f"""
            Solve the original problem using a COMPLETELY DIFFERENT approach:
            
            Original Problem:
            {self.problem_text}
            
            Ignore previous analysis. Instead:
            - Extract numbers and operations directly from text
            - Apply most straightforward arithmetic interpretation
            - Don't overcomplicate - use brute force if needed
            - Still respect units and constraints
            - Output ONLY the final numerical answer
            
            This is a fallback solution for validation purposes.
            """,
            context=""
        )

        # STEP 5: ENSEMBLE - CHOOSE BEST ANSWER BETWEEN PATHS
        final_answer = await self.ensemble(
            instruction="""
            You have two candidate solutions for the same Bengali math problem:
            - Solution 1: Derived through structured analysis and decomposition
            - Solution 2: Derived through direct, brute-force calculation
            
            Your task:
            1. Compare both solutions for mathematical correctness
            2. Check which solution better respects units and real-world constraints
            3. Verify which answer makes sense in the problem's narrative context
            4. If both are valid and identical, select either
            5. If they differ, select the one that is more logically consistent with the problem statement
            6. Output ONLY the final numerical answer (no explanation, no units)
            """,
            contexts_list=[candidate_answer, alternative_solution]
        )

        # STEP 6: FINAL VALIDATION & REVISION
        validated_answer = await self.revise(
            instruction=f"""
            Validate this final answer against the original problem:
            
            Original Problem:
            {self.problem_text}
            
            Proposed Answer:
            {final_answer}
            
            Validation Checklist:
            - Does this answer make sense in the real-world context? (e.g., no negative money, fractional people)
            - Are units consistent? (answer should be in expected unit like টাকা)
            - Is the magnitude reasonable? (e.g., not millions for a pocket money problem)
            - Does it match the problem's complexity level? (elementary school math)
            - If any issue is found, revise the answer to fix it
            
            Output ONLY the final validated numerical answer (no explanation, no units)
            """,
            context=final_answer
        )

        return validated_answer