# Workflow ID: mgsmbn_22_0
# Benchmark: mgsmbn
# Data Indices: [186, 21]

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

        # PHASE 1: PROBLEM CLASSIFICATION & ROUTING
        classification = await self.generate(
            instruction="""Thoroughly classify this Bengali math problem:
            1. Complexity Level: Simple (direct operations) or Complex (multi-step, relational, algebraic)
            2. Entity Types: Identify all people, objects, quantities, and units (e.g., টাকা, ডলার, ঝিনুক)
            3. Operation Types: List required operations (addition, multiplication, comparison, etc.)
            4. Hidden Steps: Are there implicit calculations or dependencies?
            5. Answer Constraints: Must answer be integer? Non-negative? Unit-specific?
            Output in structured JSON-like format with keys: complexity, entities, operations, hidden_steps, constraints.""",
            context=""
        )

        # CONDITIONAL BRANCH: Simple vs Complex Path
        if "simple" in classification.lower() and "complex" not in classification.lower():
            # SIMPLE PATH: Direct translation to code
            direct_solution = await self.programmer(
                instruction=f"""Solve directly using basic arithmetic. 
                Problem context: {classification}
                Rules:
                - Define variables with explicit units (e.g., shells_collected, dollars_spent)
                - Validate dimensional consistency
                - If result is negative/fractional in discrete context, throw ValueError
                - Return ONLY the final numerical answer as float or int""",
                context=""
            )
            # Extract number from programmer output
            match = re.search(r'[\d\.]+', direct_solution)
            return float(match.group()) if match else direct_solution

        else:
            # COMPLEX PATH: Full Adaptive Semantic-Computational Cascade
            
            # PHASE 2: SEMANTIC DECOMPOSITION
            decomposition = await self.decompose(
                instruction="""Break problem into minimal, ordered subproblems. For each:
                - ID: Sequential identifier (step_1, step_2, ...)
                - Description: What is being calculated? (Subject + Action + Operands + Operation)
                - Dependencies: Which prior steps must be completed? (comma-separated IDs)
                - Units: What are the units of the result?
                - Constraints: Any physical/logical constraints (e.g., non-negative, integer)
                Format each as dictionary with keys: id, description, dependencies, units, constraints""",
                context=classification
            )

            # PHASE 3: PARALLEL SYMBOLIC MODELING
            modeling_tasks = []
            for i, subproblem in enumerate(decomposition):
                modeling_tasks.append(
                    self.generate(
                        instruction=f"""Convert this subproblem into executable mathematical representation:
                        Subproblem: {subproblem['description']}
                        Dependencies: {subproblem.get('dependencies', '')}
                        Units: {subproblem.get('units', 'unitless')}
                        Constraints: {subproblem.get('constraints', 'none')}
                        
                        Output format:
                        VARIABLE_NAME_units = OPERATION(EXPRESSION)
                        Example: kylie_shells_monday = robert_shells_monday + 5
                        
                        Rules:
                        - Use snake_case variable names with units suffix
                        - Reference only variables from dependency steps
                        - Include unit conversion if needed
                        - If operation is ambiguous, provide 2 interpretations""",
                        context=subproblem['description']
                    )
                )
            
            symbolic_models = await asyncio.gather(*modeling_tasks)

            # PHASE 4: DEPENDENCY-AWARE SYNTHESIS
            synthesis = await self.ensemble(
                instruction=f"""Synthesize all symbolic models into one coherent computational graph:
                - Resolve variable references across steps
                - Order steps by dependency (topological sort)
                - Flag any circular dependencies or undefined variables
                - Merge redundant variables
                - Ensure unit consistency across operations
                - If multiple interpretations exist, select most contextually plausible
                Output: Ordered list of variable assignments ready for code execution""",
                contexts_list=symbolic_models
            )

            # PHASE 5: CODE GENERATION WITH VALIDATION
            final_answer = None
            error_context = ""
            
            for attempt in range(3):  # Max 3 retries
                try:
                    code_solution = await self.programmer(
                        instruction=f"""Execute this computational graph:
                        {synthesis}
                        
                        Rules:
                        1. Define all variables explicitly with units in name (e.g., price_dollars)
                        2. Validate dimensional consistency before each operation
                        3. If units mismatch, throw ValueError with details
                        4. If result violates constraints (negative/fractional in discrete context), throw ValueError
                        5. Print ONLY the final numerical answer (no text, no units)
                        6. Use float for decimals, int for whole numbers""",
                        context=synthesis + error_context
                    )
                    
                    # Extract numerical answer
                    match = re.search(r'[\d\.]+', code_solution)
                    if match:
                        final_answer = float(match.group())
                        break
                    else:
                        error_context = f"\nPrevious attempt failed: {code_solution}"
                        
                except Exception as e:
                    error_context = f"\nError: {str(e)}. Revise decomposition."
                    # Trigger revision of decomposition
                    revised_decomposition = await self.revise(
                        instruction=f"""Fix decomposition based on error:
                        Error: {str(e)}
                        Original decomposition: {decomposition}
                        Rules:
                        - Reorder steps to resolve dependency issues
                        - Clarify ambiguous operations
                        - Add missing constraints
                        - Ensure all variables are defined before use""",
                        context=str(decomposition)
                    )
                    # Update decomposition and retry
                    decomposition = await self.decompose(
                        instruction="Revised decomposition based on error feedback. Follow same format.",
                        context=revised_decomposition
                    )
                    # Regenerate models
                    modeling_tasks = [
                        self.generate(
                            instruction=f"Regenerate model for: {sub['description']}",
                            context=sub['description']
                        ) for sub in decomposition
                    ]
                    symbolic_models = await asyncio.gather(*modeling_tasks)
                    synthesis = await self.ensemble(
                        instruction="Resynthesize with revised decomposition",
                        contexts_list=symbolic_models
                    )

            if final_answer is None:
                # FALLBACK: Generate answer through reasoning
                fallback = await self.generate(
                    instruction="Solve step by step through reasoning. Show calculations. Box final answer.",
                    context=classification
                )
                match = re.search(r'[\d\.]+', fallback)
                final_answer = float(match.group()) if match else 0.0

            return final_answer