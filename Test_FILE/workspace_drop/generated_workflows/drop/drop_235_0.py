# Workflow ID: drop_235_0
# Benchmark: drop
# Data Indices: [3261, 1624, 989, 2676]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on numerical data, time spans, or specific events mentioned.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Perform necessary calculations or comparisons based on the extracted data (e.g., subtract start year from end year, compare pass lengths).</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify that the calculated answer aligns with the context of the question and the passage.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Return the final answer as a single, clear value.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>