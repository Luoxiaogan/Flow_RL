# Workflow ID: hotpotqa_538_0
# Benchmark: hotpotqa
# Data Indices: [435, 2524, 2225, 1430, 3850]

<node id="1" type="input">
        <prompt>Understand the core question and identify key entities mentioned in the context.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on specific details like names, locations, or events tied to the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that the extracted information matches the exact requirement of the question—no assumptions or generalizations.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Check for any potential ambiguity or multiple possible answers in the context and resolve them using logical consistency.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the validated extraction and verification steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>