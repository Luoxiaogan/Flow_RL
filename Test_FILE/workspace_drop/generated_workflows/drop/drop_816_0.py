# Workflow ID: drop_816_0
# Benchmark: drop
# Data Indices: [3030, 1414, 369, 3825, 3996]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Identify key events, counts, or percentages mentioned.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific metric the question asks for (e.g., field goals, households, years, touchdowns). Filter extracted_data to match this metric.</instruction>
        <input>extracted_data</input>
        <output>filtered_data</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Perform necessary calculations (e.g., summing field goals, computing percentages, finding time differences) using filtered_data.</instruction>
        <input>filtered_data</input>
        <output>calculated_result</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Verify that the calculated result matches the question's requirement and is consistent with the passage context. Ensure no misinterpretation occurred.</instruction>
        <input>calculated_result</input>
        <output>final_answer</output>
    </node>
    
    <node id="6" type="output">
        <param name="answer" type="str"/>
        <input>final_answer</input>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>