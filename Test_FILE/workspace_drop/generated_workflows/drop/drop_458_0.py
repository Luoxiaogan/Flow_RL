# Workflow ID: drop_458_0
# Benchmark: drop
# Data Indices: [1609, 2838, 2346, 579, 1085]

<node id="1" type="input">
        <prompt>Read the problem carefully and identify the key information needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract numerical values and relevant entities from the passage. Focus on quantities, scores, or time periods mentioned.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Identify the specific question being asked and determine what operation (addition, subtraction, comparison, etc.) is required to find the answer.</prompt>
    </node>
    
    <node id="4" type="operator">
        <prompt>Apply the correct mathematical or logical operation based on the extracted data and question type.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>Verify that the computed result matches the context of the question and makes sense in the scenario described.</prompt>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the final answer as a single number or clear statement based on the verified result.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>