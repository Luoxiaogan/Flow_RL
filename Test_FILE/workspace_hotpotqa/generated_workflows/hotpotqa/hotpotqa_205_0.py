# Workflow ID: hotpotqa_205_0
# Benchmark: hotpotqa
# Data Indices: [279, 1620, 2654, 3156, 3692]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities and relationships.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Identify the main subject of the question and locate relevant context clues.</prompt>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="agent">
        <prompt>Trace connections between the subject and other known entities (e.g., bands, cities, events).</prompt>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="agent">
        <prompt>Determine which entity from the context matches the required criteria (e.g., band formed in 2001, shared bill with The Jepettos at Tennent's Vital in 2012).</prompt>
        <dependencies>3</dependencies>
    </node>
    
    <node id="5" type="agent">
        <prompt>From the identified band, extract the state they are from based on the provided context.</prompt>
        <dependencies>4</dependencies>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the state associated with the band that matches all given conditions.</prompt>
        <dependencies>5</dependencies>
    </node>