# Workflow ID: mbppplus_83_0
# Benchmark: mbppplus
# Data Indices: [373, 210, 196]

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

        # STEP 1: CLASSIFY PROBLEM TYPE & EXTRACT STRUCTURE
        classification = await self.generate(
            instruction="""Analyze this programming problem with extreme precision. Your task:

1. Classify the problem into exactly one primary category:
   - "LIST_TUPLE_OPS" (filtering, transformations, common elements)
   - "STRING_MANIP" (parsing, formatting, pattern matching)
   - "MATH_SEQ" (number theory, arithmetic, sequences, ranges)
   - "DATA_STRUCT_ALGO" (searching, sorting, DP, graph-like structures)
   - "LOGIC_VALIDATION" (comparisons, conditionals, boolean outcomes)

2. Identify key structural elements:
   - Input types (list, tuple, int, str, nested structures)
   - Output type and format requirements
   - Implied algorithmic patterns (e.g., DP, greedy, brute-force)
   - Critical edge cases (empty inputs, single elements, duplicates, negatives)

3. Extract any mathematical formulas or invariants mentioned or implied.

4. Note any explicit or implicit constraints on time/space complexity.

Return your analysis in this exact JSON format:
{
  "category": "CATEGORY_NAME",
  "input_types": ["type1", "type2"],
  "output_type": "type",
  "algorithm_hints": ["hint1", "hint2"],
  "edge_cases": ["case1", "case2"],
  "constraints": ["constraint1"]
}""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION (3 TRACKS)
        strategy_instructions = {
            "MATH_SEQ": """You are a mathematical optimization expert. Derive a closed-form formula or efficient mathematical shortcut. Avoid brute-force iteration. Handle negative numbers, zero, and overflow. Show derivation steps. Return ONLY the function implementation with imports inside.""",
            "DATA_STRUCT_ALGO": """You are a dynamic programming and algorithms specialist. Model this as a state transition problem. Use memoization or tabulation. Optimize for time complexity. Handle boundary conditions explicitly. Return ONLY the function implementation with imports inside.""",
            "LOGIC_VALIDATION": """You are a strict type and structure validator. Implement exact equality or logical comparison. Preserve order, handle nested structures, consider type coercion pitfalls. Return ONLY the function implementation with imports inside.""",
            "LIST_TUPLE_OPS": """You are a data transformation expert. Use list comprehensions, built-in functions, or itertools for efficiency. Handle empty lists, duplicates, and type consistency. Return ONLY the function implementation with imports inside.""",
            "STRING_MANIP": """You are a string processing guru. Use regex, slicing, or built-in methods optimally. Handle empty strings, unicode, and edge delimiters. Return ONLY the function implementation with imports inside."""
        }

        # Get category from classification (with fallback)
        try:
            classification_data = json.loads(classification)
            category = classification_data.get("category", "LOGIC_VALIDATION")
        except:
            category = "LOGIC_VALIDATION"

        # Generate 3 parallel solution attempts (primary + 2 alternatives)
        primary_instruction = strategy_instructions.get(category, strategy_instructions["LOGIC_VALIDATION"])
        alternative_categories = [k for k in strategy_instructions.keys() if k != category][:2]
        
        solution_tasks = [
            self.generate(instruction=primary_instruction, context=""),
            self.generate(instruction=strategy_instructions.get(alternative_categories[0], strategy_instructions["LOGIC_VALIDATION"]), context="") if alternative_categories else None,
            self.generate(instruction=strategy_instructions.get(alternative_categories[1], strategy_instructions["LOGIC_VALIDATION"]), context="") if len(alternative_categories) > 1 else None
        ]
        
        # Filter out None tasks
        solution_tasks = [task for task in solution_tasks if task is not None]
        solutions = await asyncio.gather(*solution_tasks)

        # STEP 3: VALIDATION & REFINEMENT LOOP
        validated_solutions = []
        for sol in solutions:
            # Validation step
            validation = await self.generate(
                instruction=f"""Rigorously validate this solution against the problem requirements:

1. Check against these edge cases: {classification_data.get('edge_cases', ['empty input', 'single element'])}
2. Verify return type matches exactly: {classification_data.get('output_type', 'any')}
3. Test against sample assertions from problem (if any provided)
4. Check for common pitfalls: type mismatches, off-by-one errors, unhandled exceptions
5. Ensure imports are inside function if required

Return JSON: {{"valid": true/false, "issues": ["list of specific issues"], "confidence": 0.0-1.0}}""",
                context=sol
            )
            
            try:
                validation_data = json.loads(validation)
                if not validation_data.get("valid", False) and validation_data.get("confidence", 0) < 0.8:
                    # Revise if validation fails
                    revised = await self.revise(
                        instruction=f"""Fix ALL identified issues:
{validation_data.get('issues', [])}

Requirements:
- Handle edge cases: {classification_data.get('edge_cases', [])}
- Return type: {classification_data.get('output_type', 'any')}
- Match function signature exactly
- Include necessary imports INSIDE function
- Return ONLY the raw function code, no explanations""",
                        context=sol
                    )
                    validated_solutions.append(revised)
                else:
                    validated_solutions.append(sol)
            except:
                # If validation fails, keep original but flag for ensemble
                validated_solutions.append(sol)

        # STEP 4: ENSEMBLE SYNTHESIS
        final_solution = await self.ensemble(
            instruction="""Synthesize the best final solution from these candidates:

Evaluation criteria (in order of priority):
1. Correctness: Must handle all edge cases identified in classification
2. Type fidelity: Return type and structure must match problem requirements exactly
3. Robustness: Graceful handling of invalid inputs (if specified)
4. Efficiency: Prefer mathematical shortcuts over brute-force when equivalent
5. Code quality: Clean, readable, minimal dependencies

If multiple solutions are valid, prefer the one with:
- Most explicit edge-case handling
- Highest validation confidence score
- Most efficient algorithmic approach

Return ONLY the raw function implementation. NO explanations, NO markdown, NO additional text. Strip all comments if they exist. Ensure imports are inside the function if required.""",
            contexts_list=validated_solutions
        )

        # STEP 5: FINAL SANITIZATION
        sanitized = await self.revise(
            instruction="""STRICT OUTPUT SANITIZATION:
- Extract ONLY the function implementation code
- Remove ALL explanatory text, comments, markdown formatting
- Ensure function signature matches original exactly
- Place ALL imports inside the function body if present
- Return NOTHING except the raw code block
- If no valid function exists, return the most plausible candidate""",
            context=final_solution
        )

        return sanitized