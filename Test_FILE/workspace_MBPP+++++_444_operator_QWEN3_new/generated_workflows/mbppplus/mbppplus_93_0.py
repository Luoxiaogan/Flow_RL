# Workflow ID: mbppplus_93_0
# Benchmark: mbppplus
# Data Indices: [52, 102, 236]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # Phase 1: Parallel Problem Decomposition
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from a DATA STRUCTURE perspective:
                - Identify input/output types (list, dict, tuple, number, string)
                - Map required transformations or operations
                - List potential edge cases (empty inputs, single elements, duplicates, type boundaries)
                - Suggest appropriate Python constructs (defaultdict, set operations, list comprehensions, etc.)
                Format as structured JSON with keys: "input_type", "output_type", "edge_cases", "recommended_approach\"""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL/LOGICAL perspective:
                - Identify any numerical sequences, formulas, or patterns
                - Derive underlying mathematical relationships
                - Consider computational complexity and efficiency
                - Note any invariants or constraints that must be preserved
                Format as structured JSON with keys: "mathematical_pattern", "formula", "complexity", "invariants\"""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a ROBUSTNESS/EDGE CASE perspective:
                - Enumerate all possible failure modes
                - Identify boundary conditions (min/max values, empty structures, None inputs)
                - Suggest defensive programming techniques
                - Propose validation strategies for generated solutions
                Format as structured JSON with keys: "failure_modes", "boundary_conditions", "defensive_techniques", "validation_strategy\"""",
                context=""
            )
        ]
        
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        
        # Phase 2: Parallel Solution Generation
        solution_tasks = []
        for i, analysis in enumerate(decomposition_results):
            solution_tasks.append(
                self.generate(
                    instruction=f"""Generate a complete Python function solution based on this analysis:
                    {analysis}
                    
                    Requirements:
                    - Handle all edge cases mentioned in the analysis
                    - Use appropriate data structures and algorithms
                    - Include necessary imports
                    - Match exact function signature from problem
                    - Prioritize correctness over brevity
                    - Add inline comments explaining key decisions
                    - Return correct data type as specified
                    
                    Output ONLY the Python function code, nothing else.""",
                    context=analysis
                )
            )
        
        candidate_solutions = await asyncio.gather(*solution_tasks)
        
        # Phase 3: Parallel Validation & Refinement
        validation_tasks = []
        for i, solution in enumerate(candidate_solutions):
            validation_tasks.append(
                self.revise(
                    instruction=f"""Critically validate this solution:
                    {solution}
                    
                    Validation Protocol:
                    1. Construct 3-5 test cases including edge cases from analysis
                    2. Verify correctness against problem requirements
                    3. Check for type consistency and boundary handling
                    4. Identify any logical flaws or efficiency issues
                    5. If flaws found, provide corrected version with explanations
                    6. If no flaws, output "VALIDATED" followed by original solution
                    
                    Output format: 
                    VALIDATION REPORT: [summary of tests and results]
                    CORRECTED SOLUTION: [fixed code if needed, otherwise original]""",
                    context=solution
                )
            )
        
        validated_solutions = await asyncio.gather(*validation_tasks)
        
        # Extract corrected solutions
        final_candidates = []
        for validation in validated_solutions:
            if "CORRECTED SOLUTION:" in validation:
                solution_part = validation.split("CORRECTED SOLUTION:")[1].strip()
                final_candidates.append(solution_part)
            else:
                # Assume original solution if no correction mentioned
                final_candidates.append(validation)
        
        # Phase 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            - Prioritize correctness and edge case handling above all
            - Choose the most readable and maintainable implementation
            - Ensure type consistency and proper imports
            - If candidates have complementary strengths, merge them
            - Output ONLY the final Python function code, nothing else
            
            Evaluation Criteria:
            1. Completeness: Handles all specified and implied requirements
            2. Robustness: Gracefully handles edge cases and invalid inputs
            3. Efficiency: Uses appropriate algorithms and data structures
            4. Clarity: Code is readable with meaningful variable names
            5. Compliance: Matches exact function signature and return type""",
            contexts_list=final_candidates
        )
        
        # Phase 5: Final Safety Check
        final_check = await self.revise(
            instruction="""Perform final safety verification:
            - Ensure output is ONLY Python function code with no explanations
            - Verify function signature matches problem exactly
            - Confirm all necessary imports are included
            - Check for any remaining placeholders or TODOs
            - Ensure no print statements or debug code remains
            - Validate indentation and syntax correctness
            
            If any issues found, fix them. Otherwise, return unchanged.""",
            context=final_solution
        )
        
        return final_check