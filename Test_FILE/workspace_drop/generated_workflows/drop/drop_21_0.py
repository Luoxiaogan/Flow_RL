# Workflow ID: drop_21_0
# Benchmark: drop
# Data Indices: [414, 3020, 116, 855, 1878]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and numerical data relevant to the question. Extract all values related to the specific query (e.g., field goals, yards, team names).</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Compare or calculate based on the extracted values. For example, subtract one quantity from another or find the maximum value among a list.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the computed result aligns with the question's requirement. Ensure no misinterpretation of units or context (e.g., field goal vs. touchdown pass).</instruction>
    </node>
    <node id="5" type="output">
        <description>Return the final answer as a single number or string based on the computation.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>