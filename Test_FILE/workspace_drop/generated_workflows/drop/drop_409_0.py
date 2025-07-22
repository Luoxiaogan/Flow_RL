# Workflow ID: drop_409_0
# Benchmark: drop
# Data Indices: [1783, 2005, 1841, 1223, 2]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities or values to extract.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific names, numbers, or events mentioned in relation to the query.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if multiple pieces of information are needed to answer the question fully. If so, locate each piece systematically.</prompt>
    </node>
    
    <node id="4" type="operator">
        <prompt>Use logical grouping or filtering to isolate exact values (e.g., yardage for Lewis and Baskett) based on context clues like "each had over 100 yards receiving".</prompt>
    </node>
    
    <node id="5" type="operator">
        <prompt>Apply conditional logic: if a name appears in a list with a shared metric (like >100 yards), determine individual values using supporting details (e.g., "Jackson, Lewis, and Baskett each had over 100 yards").</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the final answer as a structured response—ensure it matches exactly what was asked (e.g., "Lewis: X yards, Baskett: Y yards").</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>