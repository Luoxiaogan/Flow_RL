# Workflow ID: hotpotqa_545_0
# Benchmark: hotpotqa
# Data Indices: [698, 1675, 1352, 1630]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context for each entity mentioned in the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Compare the attributes (e.g., age, birth year) of the entities to determine which is younger.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the comparison by cross-referencing with multiple sources or contexts if available.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the correct answer based on the verified comparison.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>