# Workflow ID: mgsmbn_24_0
# Benchmark: mgsmbn
# Data Indices: [47, 83]

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
        
        # Step 1: Assess complexity to determine workflow depth
        complexity_analysis = await self.generate(
            instruction="""Analyze this Bengali math problem and classify its complexity:
            - Count the number of distinct mathematical operations required
            - Identify if there are multiple entities or sequential dependencies
            - Note if any steps are implicit or require inference
            - Determine if unit conversions or proportional reasoning is involved
            - Output format: "Complexity: [Low/Medium/High] | Operations: [N] | Entities: [List] | Flags: [implicit,units,proportional,...]"
            Keep analysis concise but comprehensive.""",
            context=""
        )
        
        # Step 2: Decompose problem into subproblems with dependencies
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems.
            For each subproblem:
            - State it as a clear mathematical question
            - Specify what inputs it needs (referencing other subproblem IDs if dependent)
            - Note required operations and units
            - Flag if it involves fractions, percentages, or unit conversions
            Prioritize logical order and dependency resolution.""",
            context=complexity_analysis
        )
        
        # Step 3: Topological sort of subproblems by dependency
        def topological_sort(subproblems):
            id_to_index = {sp['id']: i for i, sp in enumerate(subproblems)}
            graph = {sp['id']: sp.get('dependencies', '').split(',') if sp.get('dependencies') else [] for sp in subproblems}
            indegree = {node: 0 for node in graph}
            for deps in graph.values():
                for dep in deps:
                    if dep.strip():
                        indegree[dep.strip()] += 1
            
            queue = [node for node in indegree if indegree[node] == 0]
            result = []
            while queue:
                node = queue.pop(0)
                result.append(node)
                for next_node, deps in graph.items():
                    if node in deps:
                        indegree[next_node] -= 1
                        if indegree[next_node] == 0:
                            queue.append(next_node)
            return [subproblems[id_to_index[nid]] for nid in result]
        
        sorted_subproblems = topological_sort(decomposition)
        
        # Step 4: Solve each subproblem with formalization + code execution
        subproblem_solutions = {}
        for subproblem in sorted_subproblems:
            sp_id = subproblem['id']
            
            # Generate mathematical formalization
            formalization = await self.generate(
                instruction=f"""Convert this subproblem into precise mathematical form:
                Subproblem: {subproblem['description']}
                Dependencies: {subproblem.get('dependencies', 'None')}
                Available prior solutions: {list(subproblem_solutions.items())}
                
                Requirements:
                - Define all variables explicitly
                - Write equations or expressions
                - Preserve units throughout
                - If proportional, show ratio setup
                - Output ONLY the mathematical representation, no explanations.""",
                context=subproblem['description']
            )
            
            # Generate and execute code for solution
            code_solution = await self.programmer(
                instruction=f"""Solve this mathematical subproblem using Python:
                Formalization: {formalization}
                Dependencies: {subproblem.get('dependencies', 'None')}
                Prior solutions: {subproblem_solutions}
                
                Requirements:
                - Use exact arithmetic (fractions if needed)
                - Track and validate units
                - Handle edge cases (negative values, division by zero)
                - Output ONLY the numerical result with unit if applicable
                - If error, return 'ERROR: [description]'""",
                context=formalization,
                max_retries=3
            )
            
            # Extract numerical result
            match = re.search(r'([-+]?\d*\.?\d+)', code_solution)
            if match:
                subproblem_solutions[sp_id] = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
            else:
                subproblem_solutions[sp_id] = f"ERROR: {code_solution}"
        
        # Step 5: Ensemble final answer from subproblem solutions
        final_candidates = []
        for attempt in range(2):  # Generate 2 solution narratives
            narrative = await self.generate(
                instruction=f"""Construct the complete solution narrative:
                Subproblem solutions: {subproblem_solutions}
                Original problem: {self.problem_text}
                
                Requirements:
                - Show step-by-step reasoning
                - Verify unit consistency
                - Check real-world plausibility
                - Output final answer as: "FINAL_ANSWER: [number]"
                - If inconsistency found, explain and adjust""",
                context=str(subproblem_solutions)
            )
            final_candidates.append(narrative)
        
        # Synthesize best answer
        final_answer_text = await self.ensemble(
            instruction="""Select the most accurate and complete solution:
            - Prefer solutions with explicit unit tracking
            - Prefer solutions that handle edge cases
            - Verify mathematical consistency
            - Ensure answer matches problem's real-world constraints
            - Output ONLY the final numerical answer, no explanations""",
            contexts_list=final_candidates
        )
        
        # Extract and return final numerical answer
        final_match = re.search(r'([-+]?\d*\.?\d+)', final_answer_text)
        if final_match:
            result = float(final_match.group(1)) if '.' in final_match.group(1) else int(final_match.group(1))
        else:
            # Fallback: use last subproblem solution
            last_solution = list(subproblem_solutions.values())[-1]
            if isinstance(last_solution, (int, float)):
                result = last_solution
            else:
                result = 0  # Ultimate fallback
        
        return result