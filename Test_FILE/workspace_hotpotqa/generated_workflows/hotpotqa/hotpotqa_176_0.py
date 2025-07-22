# Workflow ID: hotpotqa_176_0
# Benchmark: hotpotqa
# Data Indices: [1658, 2578, 3242, 2530, 241]

<node id="1" type="input">
        <prompt>Understand the problem statement and identify key entities.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the question. Focus on direct connections between entities mentioned in the question.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further inference.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>If indirect, trace relationships through intermediate entities (e.g., marriage, collaboration, role) to reach the final answer.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>Ensure the final answer is uniquely identifiable and matches the format required by the question.</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the correct answer based on the chain of reasoning.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>