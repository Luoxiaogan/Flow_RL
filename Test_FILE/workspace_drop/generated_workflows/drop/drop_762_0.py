# Workflow ID: drop_762_0
# Benchmark: drop
# Data Indices: [3022, 2612, 2505, 1251, 1486]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical values from the passage that are needed to answer the question.</instruction>
        <param name="input">1</param>
        <output>extracted_values</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific calculation required based on the question and the extracted values. Think step by step: determine which numbers represent the quantities being compared or operated on.</instruction>
        <param name="input">2</param>
        <output>calculation_logic</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Perform the mathematical operation using the identified logic. Ensure precision and correctness of the arithmetic, especially with differences, ratios, or sums.</instruction>
        <param name="input">3</param>
        <output>result</output>
    </node>
    
    <node id="5" type="output">
        <param name="input">4</param>
        <param name="format">Answer: {result}</param>
    </node>