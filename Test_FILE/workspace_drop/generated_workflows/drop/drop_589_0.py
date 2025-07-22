# Workflow ID: drop_589_0
# Benchmark: drop
# Data Indices: [3239, 878, 2093, 2410]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage. Identify all percentages and counts mentioned.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific question being asked. Determine which values in the extracted data are needed to answer it.</instruction>
        <input>1</input>
        <input>2</input>
        <output>relevant_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary calculations using the relevant values. If a percentage is requested, compute it based on total or given parts.</instruction>
        <input>3</input>
        <output>calculation_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the calculation logic and ensure the final answer matches the question's requirement exactly (e.g., percent, count, difference).</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>