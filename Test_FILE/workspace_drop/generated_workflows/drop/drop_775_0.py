# Workflow ID: drop_775_0
# Benchmark: drop
# Data Indices: [3827, 1998, 920, 3016, 3445]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage related to the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Compare or analyze the extracted data to answer the specific question.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Provide the final answer based on the analysis.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>