# Workflow ID: hotpotqa_166_0
# Benchmark: hotpotqa
# Data Indices: [1518, 3245, 3005, 2848]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the film based on Yury Tynyanov's novella and its US release title.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the connection between the novella, film, and US title.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Confirm the correct US title from the provided context.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the US release title of the film based on Yury Tynyanov's novella.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>