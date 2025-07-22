# Workflow ID: drop_561_0
# Benchmark: drop
# Data Indices: [2731, 457, 3669, 45]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data related to the question in the passage. Focus on values that directly answer the query, such as scores, yardages, or age percentages.</instruction>
        <input>problem</input>
        <output>key_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract and isolate the specific value that answers the question from the key data. Ensure it is correctly interpreted based on context (e.g., points, yards, or percentage).</instruction>
        <input>key_data</input>
        <output>answer_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the extracted value by cross-checking with the original passage to ensure accuracy and avoid misinterpretation.</instruction>
        <input>answer_value</input>
        <input>problem</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <param>final_answer</param>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>