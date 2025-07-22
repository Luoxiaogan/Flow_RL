# Workflow ID: drop_846_0
# Benchmark: drop
# Data Indices: [1537, 3232, 498, 3422]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to answer it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific numbers, names, or events mentioned in relation to the query.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Compare and contrast the extracted data points to determine the least frequent or most distinct category (for problems like Problem 1) or the final event (for Problems 2–4).</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify that the selected answer matches the exact wording or context of the question — for example, if the question asks "who scored the last touchdown," ensure the agent identifies the correct player and game context.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer based on the consensus from the previous agents. Ensure clarity and precision.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>