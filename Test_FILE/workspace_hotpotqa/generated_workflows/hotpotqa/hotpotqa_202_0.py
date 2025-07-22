# Workflow ID: hotpotqa_202_0
# Benchmark: hotpotqa
# Data Indices: [2201, 271, 3666, 52, 243]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities and relationships.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the American actor who was on MADtv and starred in Suicide Squad. Focus on the actor's name and filmography.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Find the 2016 comedy film co-written by that actor. Use the context to locate the title and its cast.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Determine who starred in that specific film. Extract all main actors from the context provided.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the list of actors who starred in the 2016 comedy film co-written by the MADtv alumnus who also appeared in Suicide Squad.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>