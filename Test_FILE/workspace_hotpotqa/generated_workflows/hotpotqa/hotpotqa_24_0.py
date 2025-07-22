# Workflow ID: hotpotqa_24_0
# Benchmark: hotpotqa
# Data Indices: [1388, 2885, 3250, 1547]

<node id="1" type="input">
        <prompt>Understand the core question and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the key entities. Focus on direct connections or explicit mentions.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against known facts or logical consistency in the context.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Combine verified information to form a coherent answer, ensuring no contradictions.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the synthesized information from previous nodes.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>