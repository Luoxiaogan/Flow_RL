# Workflow ID: drop_412_0
# Benchmark: drop
# Data Indices: [2776, 853, 744, 3184, 3672]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract key entities and timeline from the passage. Identify events, dates, and relationships between them.</instruction>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="agent">
        <instruction>Map each event to a chronological order based on temporal indicators (e.g., "in April 1943", "on 21 June"). Ensure no contradictions in sequence.</instruction>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="agent">
        <instruction>Identify the specific question being asked and locate relevant information in the timeline.</instruction>
        <dependencies>3</dependencies>
    </node>
    
    <node id="5" type="agent">
        <instruction>Calculate the difference between two relevant time points if the question involves duration or interval.</instruction>
        <dependencies>4</dependencies>
    </node>
    
    <node id="6" type="output">
        <description>Return the final answer based on the computed result from node 5.</description>
        <dependencies>5</dependencies>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>