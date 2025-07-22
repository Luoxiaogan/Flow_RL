# Workflow ID: hotpotqa_378_0
# Benchmark: hotpotqa
# Data Indices: [1165, 1062, 797, 738]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the key entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that the extracted information directly answers the question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Check for any indirect clues or additional context that may help confirm the answer.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Ensure no irrelevant data is included in the final response.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the correct answer based on verified information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>