# Workflow ID: hotpotqa_335_0
# Benchmark: hotpotqa
# Data Indices: [2823, 81, 2397, 3241]

<node id="1" type="input">
        <instruction>Receive the problem input and initialize processing.</instruction>
    </node>
    <node id="2" type="agent">
        <instruction>Extract key entities and context from the problem. Focus on identifying the main subject, related terms, and relevant facts.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Map each entity to its known properties or relationships using internal knowledge. Ensure no information is lost during this step.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Compare the attributes of the two subjects (e.g., nationality) based on extracted facts. Reason step-by-step to avoid incorrect assumptions.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Validate the conclusion by cross-referencing with external sources or known historical data to ensure accuracy.</instruction>
    </node>
    <node id="6" type="output">
        <instruction>Return a definitive answer: 'Yes' if both subjects share the same nationality; 'No' otherwise.</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>