# Workflow ID: mgsmbn_48_0
# Benchmark: mgsmbn
# Data Indices: [14]

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

        # STEP 1: PARALLEL PROBLEM ANALYSIS - Linguistic, Mathematical, Pedagogical
        linguistic_analysis = await self.generate(
            instruction="""Perform deep linguistic parsing of the Bengali word problem:
            - Extract all named entities (people, objects, places)
            - Identify all numerical values and their associated units (টাকা, ডজন, ঘণ্টা, দিন, সপ্তাহ, etc.)
            - Map Bengali mathematical terms to operations (যোগ, বিয়োগ, গুণ, ভাগ, শতাংশ, অনুপাত)
            - Identify temporal markers (প্রতিদিন, প্রতি সপ্তাহে, মোট) and comparative phrases (চেয়ে বেশি, অর্ধেক, দ্বিগুণ)
            - Flag any ambiguous terms or potential cultural units (মণ, বিঘা, etc.)
            - Output structured JSON-like format with clear sections""",
            context=""
        )

        mathematical_analysis = await self.generate(
            instruction="""Analyze the mathematical structure of the problem:
            - Identify the target unknown (what is being asked?)
            - List known quantities and their relationships
            - Determine required operations (sequential, proportional, distribution, comparison)
            - Suggest potential formulas or equation setups
            - Identify any hidden steps or implicit calculations
            - Consider unit conversions needed
            - Output as structured mathematical roadmap""",
            context=""
        )

        pedagogical_analysis = await self.generate(
            instruction="""Frame this problem from an elementary education perspective:
            - What grade-level concept is being tested? (e.g., multiplication, unit conversion, fractions)
            - What common student misconceptions might arise?
            - What is the expected solution approach for this grade level?
            - Should the answer be integer, decimal, or fraction?
            - Are there real-world constraints to consider? (no negative people, whole items only, etc.)
            - Output as pedagogical guidance document""",
            context=""
        )

        # STEP 2: SYNTHESIZE ANALYSES INTO UNIFIED PROBLEM UNDERSTANDING
        unified_analysis = await self.ensemble(
            instruction="""Synthesize the three analyses into a single comprehensive problem understanding:
            - Combine linguistic entities with mathematical variables
            - Align pedagogical constraints with mathematical operations
            - Resolve any conflicts between analyses
            - Create a master problem specification that includes:
                * Known values with units
                * Unknown target
                * Required operations in sequence
                * Unit conversion requirements
                * Real-world constraints
            - Format as clear, executable specification""",
            contexts_list=[linguistic_analysis, mathematical_analysis, pedagogical_analysis]
        )

        # STEP 3: DECOMPOSE INTO SUBPROBLEMS WITH DEPENDENCIES
        subproblems = await self.decompose(
            instruction=f"""Based on the unified analysis:
            {unified_analysis}

            Decompose this problem into minimal, ordered subproblems:
            - Each subproblem should be solvable independently once dependencies are met
            - Include explicit unit handling in each subproblem
            - Ensure chronological/logical ordering
            - Dependencies must be clearly specified by ID
            - Each subproblem should result in a numerical intermediate value
            - Format each as: {{'id': 'sp1', 'description': '...', 'dependencies': ''}}""",
            context=unified_analysis
        )

        # STEP 4: SOLVE SUBPROBLEMS IN PARALLEL (RESPECTING DEPENDENCIES)
        # Build dependency graph and solve in topological order
        solved_subproblems = {}
        
        # Get all subproblem IDs
        subproblem_ids = [sp['id'] for sp in subproblems]
        
        # Solve in passes until all are solved
        remaining_subproblems = subproblems.copy()
        
        while remaining_subproblems:
            current_batch = []
            current_batch_info = []
            
            # Find subproblems whose dependencies are satisfied
            for sp in remaining_subproblems[:]:  # Copy for safe removal
                deps = sp['dependencies'].split(',') if sp['dependencies'] else []
                if all(dep.strip() in solved_subproblems for dep in deps if dep.strip()):
                    current_batch.append(sp)
                    remaining_subproblems.remove(sp)
            
            if not current_batch:
                # Circular dependency or missing info - break with error
                break
            
            # Solve current batch in parallel
            solve_tasks = []
            for sp in current_batch:
                deps_context = "\n".join([f"{dep_id}: {solved_subproblems[dep_id]}" for dep_id in sp['dependencies'].split(',') if dep_id.strip() in solved_subproblems]) if sp['dependencies'] else ""
                
                task = self.programmer(
                    instruction=f"""Solve this subproblem with extreme precision:
                    Subproblem: {sp['description']}
                    Dependencies: {deps_context}
                    
                    Requirements:
                    - Show all calculation steps
                    - Maintain unit consistency throughout
                    - Verify intermediate results make sense
                    - Output ONLY the final numerical value with unit if applicable
                    - If unit conversion needed, show conversion factor
                    - Round appropriately based on pedagogical context
                    - Handle remainders or fractions as specified in problem""",
                    context=unified_analysis
                )
                solve_tasks.append(task)
            
            # Execute batch
            results = await asyncio.gather(*solve_tasks)
            
            # Store results
            for i, sp in enumerate(current_batch):
                solved_subproblems[sp['id']] = results[i]

        # STEP 5: META-VALIDATION - DOES THE SOLUTION MAKE SENSE?
        final_calculation = "\n".join([f"{sp_id}: {result}" for sp_id, result in solved_subproblems.items()])
        
        validation_analysis = await self.generate(
            instruction=f"""Critically validate the complete solution:
            Original Problem: {self.problem_text}
            Unified Analysis: {unified_analysis}
            Subproblem Solutions: {final_calculation}
            
            Check for:
            - Unit consistency throughout
            - Real-world plausibility (no negative people, fractional children, etc.)
            - Magnitude reasonableness (does 1000 dozens of eggs make sense for one person?)
            - Alignment with pedagogical expectations (grade level appropriate)
            - Arithmetic accuracy (spot check key calculations)
            - Complete answer to original question
            
            If any issues found, describe them specifically. Otherwise, confirm validation passed.""",
            context=final_calculation
        )

        # STEP 6: GENERATE TWO ALTERNATIVE SOLUTION PATHS AND ENSEMBLE
        alternative1 = await self.programmer(
            instruction=f"""Solve the original problem using a completely different approach:
            - If original was arithmetic, use algebraic equations
            - If original was step-by-step, use proportion/ratio method
            - Maintain all units and constraints
            - Show work clearly
            - Output final numerical answer""",
            context=unified_analysis
        )

        alternative2 = await self.generate(
            instruction=f"""Solve the problem using intuitive, real-world reasoning:
            - Imagine explaining to a 10-year-old
            - Use concrete examples or visualizations
            - Avoid complex notation
            - Focus on conceptual understanding
            - Derive the numerical answer through reasoning
            - Output final numerical answer""",
            context=unified_analysis
        )

        # STEP 7: FINAL ENSEMBLE AND ANSWER EXTRACTION
        final_answer_candidates = [
            solved_subproblems.get(subproblems[-1]['id'], "ERROR") if subproblems else "ERROR",
            alternative1,
            alternative2
        ]

        synthesized_answer = await self.ensemble(
            instruction="""Select the best final answer from the candidates:
            - All candidates should be mathematically equivalent
            - Prefer the simplest, most pedagogically appropriate solution
            - Ensure unit consistency and real-world plausibility
            - Extract ONLY the numerical value (integer or decimal)
            - If multiple values, choose the one that best matches problem constraints
            - Output ONLY the number, nothing else""",
            contexts_list=final_answer_candidates
        )

        # STEP 8: FINAL EXTRACTION AND CLEANUP
        # Extract numerical value using regex (handle decimals, negatives, fractions)
        match = re.search(r'(-?\d+\.?\d*)', synthesized_answer)
        if match:
            final_result = match.group(1)
            # Convert to int if whole number
            if '.' in final_result:
                final_result = float(final_result)
                if final_result.is_integer():
                    final_result = int(final_result)
            else:
                final_result = int(final_result)
            return str(final_result)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return synthesized_answer.strip()