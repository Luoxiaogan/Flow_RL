# Workflow ID: drop_649_0
# Benchmark: drop
# Data Indices: [2705, 1340, 3939, 671, 3003]

<node id="1" type="input">
        <prompt>Extract all touchdown pass distances from the passage.</prompt>
        <output>list of integers representing TD pass distances</output>
    </node>
    
    <node id="2" type="process">
        <prompt>Identify the longest and shortest touchdown pass distances from the list.</prompt>
        <output>tuple (longest, shortest)</output>
    </node>
    
    <node id="3" type="compute">
        <prompt>Calculate the difference between the longest and shortest touchdown pass distances.</prompt>
        <output>integer representing the difference in yards</output>
    </node>
    
    <node id="4" type="output">
        <prompt>Return the calculated difference as the final answer.</prompt>
        <output>integer</output>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>