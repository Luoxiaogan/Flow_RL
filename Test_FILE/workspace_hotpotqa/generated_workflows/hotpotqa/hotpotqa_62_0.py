# Workflow ID: hotpotqa_62_0
# Benchmark: hotpotqa
# Data Indices: [2178, 250, 3279, 3413]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and relevant context for the question. Think step by step to isolate the core information needed to answer the query.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Map the extracted entities to known categories or classifications in the provided context. Ensure each entity is correctly interpreted based on its role in the system.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that all necessary data points are present and aligned with the question's requirements. Cross-check for consistency across different sources in the context.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Apply logical reasoning to derive the final classification or value. Use only confirmed facts from the context to avoid assumptions.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the correct answer based on the verified and reasoned output from previous steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>