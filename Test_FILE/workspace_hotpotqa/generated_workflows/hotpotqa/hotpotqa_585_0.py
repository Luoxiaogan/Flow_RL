# Workflow ID: hotpotqa_585_0
# Benchmark: hotpotqa
# Data Indices: [1196, 3713, 3260, 3823]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities or facts needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the key entities. Focus only on direct matches or clear connections.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question. If not, look for indirect links or additional context that might clarify the connection.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Check for any ambiguity in the question or context that may require disambiguation using known facts or logical inference.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>Combine findings from previous steps to construct a coherent answer based on the strongest evidence available.</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the final answer clearly and concisely, ensuring it directly addresses the original question without unnecessary details.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>