# Workflow ID: drop_662_0
# Benchmark: drop
# Data Indices: [3343, 1812, 365, 11]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate percentages or differences as needed to compare groups or categories.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Determine which group, category, or value satisfies the condition in the question.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the result against all provided data to ensure accuracy.</instruction>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>