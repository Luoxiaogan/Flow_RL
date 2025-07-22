# Workflow ID: drop_526_0
# Benchmark: drop
# Data Indices: [3452, 316, 807, 1763, 3517]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Think step by step: first identify what is being asked, then locate the corresponding data in the passage.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Process the extracted information logically—compare values, count items, or determine relationships as required by the question.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that your reasoning aligns with the question’s requirements and that no critical detail was missed.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on the processed information. Ensure it directly addresses the original question.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>