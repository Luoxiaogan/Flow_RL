# Workflow ID: mgsmbn_73_0
# Benchmark: mgsmbn
# Data Indices: [164]

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
        
        # STEP 1: Decompose problem into structured, timeline-aware subproblems
        decomposition_instruction = """
        Systematically decompose the Bengali word problem into atomic subproblems with STRICT adherence to:
        1. Chronological order of events (use temporal markers: তারপর, পরে, এখন, শুরুতে)
        2. Entity tracking (identify all agents/objects and their state changes)
        3. Mathematical relationships (extract operations: +, -, ×, ÷, fractions, percentages)
        4. Unit consistency (tag all quantities with units: টাকা, কলম, ব্যাগ, ঘণ্টা, etc.)
        5. Dependencies (if subproblem B requires result from A, mark dependency)

        Output format per subproblem:
        - id: [sequential number]
        - description: [What changes? For whom? By how much?]
        - operation: [mathematical operation implied]
        - dependencies: [comma-separated IDs of prerequisites]
        - unit: [associated unit]

        Example for "6টি ব্যাগ নীল কলম, প্রতিটিতে 9টি":
        id: 2
        description: Janet purchases 6 bags of blue pens, each containing 9 pens
        operation: multiplication (6 × 9)
        dependencies: 1
        unit: pens
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # STEP 2: Generate canonical mathematical restatements for each subproblem
        restatement_tasks = []
        for sp in subproblems:
            restatement_instruction = f"""
            Convert this subproblem into unambiguous mathematical notation:
            Original: {sp['description']}
            Operation: {sp['operation']}
            Unit: {sp['unit']}
            
            Rules:
            - Replace Bengali entities with variables (e.g., "জ্যানেট" → J)
            - Explicitly state multiplicative relationships (e.g., "প্রতিটি ব্যাগে 9টি" → ×9)
            - Preserve unit in calculation
            - Output ONLY the mathematical expression (e.g., "J_blue = 6 × 9 pens")
            """
            task = self.generate(
                instruction=restatement_instruction,
                context=""
            )
            restatement_tasks.append(task)
        
        restatements = await asyncio.gather(*restatement_tasks)

        # STEP 3: Revise restatements for fidelity against original problem
        verification_tasks = []
        for i, (sp, restatement) in enumerate(zip(subproblems, restatements)):
            verification_instruction = f"""
            Verify mathematical restatement against original Bengali text:
            Original subproblem: {sp['description']}
            Generated restatement: {restatement}
            Original full problem: {self.problem_text}
            
            Check for:
            - Correct entity mapping
            - Accurate operation (especially multiplication/division from "প্রতি", "অর্ধেক", etc.)
            - Unit consistency
            - No added/omitted quantities
            
            If incorrect, provide corrected mathematical expression. If correct, return unchanged.
            """
            task = self.revise(
                instruction=verification_instruction,
                context=restatement
            )
            verification_tasks.append(task)
        
        verified_restatements = await asyncio.gather(*verification_tasks)

        # STEP 4: Classify problem type for adaptive solving
        classification_instruction = f"""
        Classify the overall problem type based on verified restatements:
        {chr(10).join(verified_restatements)}
        
        Categories:
        1. DIRECT: Only +, -, ×, ÷ with known quantities
        2. PROPORTIONAL: Involves fractions, percentages, ratios, scaling
        3. ALGEBRAIC: Requires solving for unknown (e.g., "শুরুতে কয়টি ছিল?")
        4. TEMPORAL: Involves rates (distance/time, work/time)
        
        Also identify:
        - Primary entity being tracked
        - Final quantity being asked
        - Any unit conversions needed
        
        Output format:
        TYPE: [category]
        TARGET: [what final answer represents]
        UNITS: [list of units involved]
        """
        classification = await self.generate(
            instruction=classification_instruction,
            context="\n".join(verified_restatements)
        )

        # STEP 5: Generate parallel solution strategies based on classification
        solution_strategies = []
        
        # Strategy 1: Step-by-step state simulation
        simulation_instruction = f"""
        Solve by simulating state changes chronologically:
        Verified restatements: {chr(10).join(verified_restatements)}
        Classification: {classification}
        
        Rules:
        - Initialize state variables for each entity
        - Apply each operation in dependency order
        - Track units at every step
        - Final output must be ONLY the numerical answer (no units, no explanation)
        - Use Python code if needed
        """
        solution_strategies.append(
            self.generate(instruction=simulation_instruction, context="")
        )

        # Strategy 2: Algebraic equation solving (if applicable)
        if "ALGEBRAIC" in classification or "PROPORTIONAL" in classification:
            algebraic_instruction = f"""
            Solve by setting up and solving equations:
            Verified restatements: {chr(10).join(verified_restatements)}
            Classification: {classification}
            
            Steps:
            1. Define unknown variable(s)
            2. Write equation(s) based on relationships
            3. Solve algebraically
            4. Output ONLY numerical answer
            
            Example for "অর্ধেক খেয়ে 10 অবশিষ্ট": x * 0.5 = 10 → x = 20
            """
            solution_strategies.append(
                self.generate(instruction=algebraic_instruction, context="")
            )

        # Strategy 3: Programmer-based calculation with unit assertions
        programmer_instruction = f"""
        Generate Python code to calculate the answer with unit tracking:
        Verified restatements: {chr(10).join(verified_restatements)}
        Classification: {classification}
        
        Requirements:
        - Define variables with units as comments
        - Include assertions for unit consistency
        - Calculate step by step following dependencies
        - Print ONLY the final numerical answer (no text, no units)
        - Handle fractions/decimals precisely
        
        Example structure:
        # Initial state
        green_pens = 22  # pens
        yellow_pens = 10  # pens
        # Purchases
        blue_pens = 6 * 9  # bags * pens_per_bag
        red_pens = 2 * 6   # bags * pens_per_bag
        # Total
        total = green_pens + yellow_pens + blue_pens + red_pens
        print(total)
        """
        solution_strategies.append(
            self.programmer(instruction=programmer_instruction, context="")
        )

        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(*solution_strategies)

        # STEP 6: Ensemble to reconcile solutions
        ensemble_instruction = f"""
        Reconcile multiple solution attempts:
        Strategies: {strategy_results}
        Original problem: {self.problem_text}
        Classification: {classification}
        
        Selection criteria:
        1. Numerical consistency across methods
        2. Adherence to unit tracking
        3. Chronological fidelity
        4. Mathematical correctness
        
        If all agree, select any. If conflict, choose the most detailed/correct.
        Output ONLY the final numerical answer (integer or decimal).
        """
        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[str(r) for r in strategy_results]
        )

        # STEP 7: Extract clean numerical answer
        # Remove any non-numeric characters (except decimal point)
        clean_answer = re.sub(r'[^\d.]', '', final_answer)
        
        # Validate it's a valid number
        try:
            float(clean_answer)
            return clean_answer
        except ValueError:
            # Fallback: return first number found in any strategy
            for result in strategy_results:
                numbers = re.findall(r'\d+\.?\d*', str(result))
                if numbers:
                    return numbers[0]
            return "0"  # Ultimate fallback