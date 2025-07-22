# Workflow ID: drop_482_0
# Benchmark: drop
# Data Indices: [2264, 338, 2352, 2205]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements that need to be extracted from the passage.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on names, actions, and sequence of events.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Identify any patterns or indicators in the text that suggest a specific answer—such as "last points," "multiple touchdowns," or "ideological lines."</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Filter out irrelevant details (e.g., background context, unrelated players or events) to narrow down to the core answer.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>For numerical questions, locate exact numbers mentioned in the passage and verify their relevance to the question.</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Combine insights from all agents to produce a precise and concise final answer based on the evidence.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>