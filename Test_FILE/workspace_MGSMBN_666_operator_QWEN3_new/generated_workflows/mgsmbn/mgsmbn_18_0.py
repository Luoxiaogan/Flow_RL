# Workflow ID: mgsmbn_18_0
# Benchmark: mgsmbn
# Data Indices: [4, 24]

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

        # PHASE 1: PARALLEL DECOMPOSITION FROM MULTIPLE PERSPECTIVES
        decomposition_attempts = await asyncio.gather(
            self.generate(
                instruction="""Decompose this Bengali math problem from a mathematical operations perspective.
                Identify:
                1. All numerical values and their semantic roles (quantities, rates, percentages, totals)
                2. Arithmetic operations required (addition, subtraction, multiplication, division, percentage)
                3. Order of operations and dependencies
                4. Hidden intermediate steps not explicitly stated
                5. Units of measurement and their consistency requirements
                Format as numbered steps with clear dependencies.""",
                context=""
            ),
            self.generate(
                instruction="""Decompose this Bengali math problem from a linguistic narrative perspective.
                Identify:
                1. Key entities (people, objects, places) and their quantities
                2. Actions and events in chronological order
                3. Conditional phrases and their mathematical implications
                4. Comparative or proportional relationships
                5. Temporal or sequential markers that indicate operation order
                Format as a story breakdown with mathematical annotations.""",
                context=""
            ),
            self.generate(
                instruction="""Decompose this Bengali math problem from a real-world context perspective.
                Identify:
                1. Physical constraints (can't have negative items, fractional people, etc.)
                2. Common sense assumptions not stated explicitly
                3. Unit conversions or consistency requirements
                4. Plausibility checks for final answer
                5. Potential edge cases or ambiguities in interpretation
                Format as context-aware analysis with validation criteria.""",
                context=""
            )
        )

        # PHASE 2: ENSEMBLE INTO UNIFIED DECOMPOSITION
        unified_decomposition = await self.ensemble(
            instruction="""Synthesize the three decomposition perspectives into a single, coherent problem breakdown.
            Requirements:
            1. Resolve conflicts between perspectives by choosing the most mathematically sound interpretation
            2. Flag any remaining ambiguities that require clarification
            3. Structure as a dependency-ordered list of subproblems
            4. Each subproblem must be solvable in isolation with clear inputs and expected outputs
            5. Include unit annotations and validation criteria for each step
            6. Preserve all critical information from all perspectives
            Output format: Numbered list with [Subproblem #], [Description], [Dependencies], [Units], [Validation Criteria]""",
            contexts_list=decomposition_attempts
        )

        # PHASE 3: STRUCTURED SUBPROBLEM SOLVING WITH CONTEXT ENRICHMENT
        # Extract subproblems (simplified parsing - in practice, use more robust extraction)
        subproblems = []
        lines = unified_decomposition.split('\n')
        current_context = ""
        
        for line in lines:
            if line.strip().startswith('[') and 'Subproblem' in line:
                # Extract subproblem description (simplified)
                subproblem_desc = line.split(']', 1)[1].strip() if ']' in line else line
                subproblems.append({
                    'description': subproblem_desc,
                    'context': current_context
                })
        
        # Solve each subproblem sequentially, enriching context
        solutions = []
        accumulated_context = ""
        
        for i, subproblem in enumerate(subproblems):
            # Generate solution attempt
            solution_attempt = await self.programmer(
                instruction=f"""Solve this subproblem from a Bengali math word problem:
                {subproblem['description']}
                
                Requirements:
                1. Show all intermediate calculations step by step
                2. Annotate all numbers with their units (টাকা, ঘণ্টা, জিনিস, etc.)
                3. Validate that operations are mathematically sound
                4. Check for unit consistency in calculations
                5. Output final answer for this subproblem with units
                6. If ambiguous, state assumptions made
                
                Previous context: {accumulated_context}""",
                context=subproblem['context']
            )
            
            # Validate solution
            validation = await self.generate(
                instruction=f"""Critically validate this subproblem solution:
                Solution: {solution_attempt}
                
                Check for:
                1. Mathematical correctness of calculations
                2. Unit consistency throughout
                3. Alignment with problem constraints
                4. Plausibility in real-world context
                5. Consistency with previous subproblem solutions
                
                If errors found, explain precisely what's wrong and how to fix it.
                If correct, confirm with "VALID: " prefix.""",
                context=accumulated_context
            )
            
            # Revise if necessary (max 1 revision per subproblem)
            if "VALID:" not in validation:
                solution_attempt = await self.revise(
                    instruction=f"""Fix the errors identified in validation:
                    Validation feedback: {validation}
                    
                    Requirements:
                    1. Correct all mathematical errors
                    2. Ensure unit consistency
                    3. Maintain step-by-step calculation visibility
                    4. Annotate all numbers with units
                    5. Output revised solution with clear indication of changes""",
                    context=solution_attempt
                )
            
            solutions.append(solution_attempt)
            accumulated_context += f"\nSubproblem {i+1} Solution: {solution_attempt}\n"
        
        # PHASE 4: FINAL SYNTHESIS AND ANSWER EXTRACTION
        final_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a final answer:
            {accumulated_context}
            
            Requirements:
            1. Trace the complete solution path from problem to answer
            2. Verify that all dependencies are satisfied
            3. Check final answer against real-world plausibility
            4. Extract ONLY the final numerical answer (with units if specified in problem)
            5. If units not specified, output number only
            6. Round appropriately based on problem context
            7. Format as: "FINAL_ANSWER: [number]" (exactly this format)""",
            context=accumulated_context
        )
        
        # Extract final answer
        final_answer_match = re.search(r'FINAL_ANSWER:\s*([0-9.]+)', final_synthesis)
        if final_answer_match:
            return final_answer_match.group(1)
        else:
            # Fallback: try to extract any number from the last solution
            last_solution = solutions[-1] if solutions else ""
            number_match = re.search(r'([0-9.]+)', last_solution)
            if number_match:
                return number_match.group(1)
            else:
                # Ultimate fallback
                return "0"