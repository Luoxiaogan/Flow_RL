# Workflow ID: drop_254_0
# Benchmark: drop
# Data Indices: [391, 3199, 1214, 3506, 1180]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Identify all instances of field goals, touchdowns, or other metrics mentioned in the text.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Filter and count only the values that match the criteria specified in the question (e.g., field goals in a specific quarter, TD passes over 12 yards).</instruction>
        <input>extracted_data</input>
        <output>filtered_count</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>For percentage change questions, calculate the difference between the two years and divide by the original value to get the percentage drop.</instruction>
        <input>extracted_data</input>
        <output>percentage_change</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Identify the first occurrence of a touchdown run by scanning through quarters in order until a run is found.</instruction>
        <input>extracted_data</input>
        <output>first_touchdown_run_quarter</output>
    </node>
    
    <node id="6" type="merge">
        <input>filtered_count</input>
        <input>percentage_change</input>
        <input>first_touchdown_run_quarter</input>
        <output>final_answer</output>
    </node>
    
    <node id="7" type="output">
        <input>final_answer</input>
    </node>