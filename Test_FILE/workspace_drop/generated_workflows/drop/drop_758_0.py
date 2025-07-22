# Workflow ID: drop_758_0
# Benchmark: drop
# Data Indices: [2251, 3311, 666, 432]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data in the passage related to the question. Extract all relevant values and their context.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>Compare the extracted values to determine which is larger or what the difference is, based on the question asked.</instruction>
        <input>2</input>
        <output>comparison_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the comparison result aligns with the question's requirement—e.g., identifying the larger group, calculating time difference, etc.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>