# Workflow ID: drop_393_0
# Benchmark: drop
# Data Indices: [2344, 258, 1881, 2659]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data relevant to the question in the passage.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Perform the necessary calculation or comparison based on the extracted data.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="output">
        <instruction>Return the final answer as a number or percentage, depending on the question.</instruction>
        <depends_on>3</depends_on>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>