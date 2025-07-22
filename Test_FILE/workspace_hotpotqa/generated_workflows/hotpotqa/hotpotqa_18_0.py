# Workflow ID: hotpotqa_18_0
# Benchmark: hotpotqa
# Data Indices: [1540, 559, 3862, 3208, 666]

<node id="1" type="input">
        <prompt>Process the given problem step by step. Identify key entities and relationships.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context that directly answers the question. Focus on named entities, dates, and actions.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Map extracted entities to known categories (e.g., nationality, ship class, profession) using contextual clues.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Validate each piece of information against the question's requirements to ensure relevance and accuracy.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Construct a logical chain connecting the validated information to derive the final answer.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer based on the derived logical chain. Ensure it precisely matches the question format.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>