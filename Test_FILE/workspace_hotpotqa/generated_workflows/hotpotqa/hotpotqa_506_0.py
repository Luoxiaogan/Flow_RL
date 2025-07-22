# Workflow ID: hotpotqa_506_0
# Benchmark: hotpotqa
# Data Indices: [3963, 2036, 7, 1723, 3122]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the key entities. Focus on direct connections between entities mentioned in the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further inference. If not, identify missing links or relationships.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Use logical reasoning to connect the verified information, especially when multiple steps are needed (e.g., "X was drafted by Y" → "Y is the team that drafted X").</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Check for consistency across all agents' outputs—ensure no contradictions exist in the final answer.</prompt>
    </node>
    <node id="6" type="agent">
        <prompt>Generate the final answer based on integrated results from previous nodes, ensuring it precisely addresses the original question.</prompt>
    </node>
    <node id="7" type="output">
        <prompt>Return the complete, accurate answer formatted clearly.</prompt>
    </node>

    <!-- Edges -->
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>
    <edge from="6" to="7"/>