# Workflow ID: hotpotqa_198_0
# Benchmark: hotpotqa
# Data Indices: [2073, 3806, 3588, 3531]

<node id="1" type="input">
        <prompt>Understand the core question and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant actors from the context who starred in both The Flight of the Phoenix and Cool Hand Luke.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if any actor from the extracted list matches both films by cross-referencing film roles.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Confirm the final answer by checking award-winning or prominent roles in both films.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the actor who starred in both The Flight of the Phoenix and Cool Hand Luke.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>