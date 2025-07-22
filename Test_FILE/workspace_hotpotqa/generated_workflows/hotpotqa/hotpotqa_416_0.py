# Workflow ID: hotpotqa_416_0
# Benchmark: hotpotqa
# Data Indices: [1604, 1541, 3359, 2065, 1434]

<node id="1" type="input">
        <prompt>Understand the core question and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant context related to each entity in the question. Focus on precise definitions or roles.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Compare the extracted information across all entities to determine if they match the category in question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify consistency of findings with known classifications or definitions from reliable sources in the context.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Formulate a clear, concise answer based on logical synthesis of evidence from previous steps.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer as a direct response to the original question.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>