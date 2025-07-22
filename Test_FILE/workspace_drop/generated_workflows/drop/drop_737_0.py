# Workflow ID: drop_737_0
# Benchmark: drop
# Data Indices: [2339, 1973, 1249, 3269]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities or values needed to solve it.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant numerical or categorical data from the passage that directly relates to the question. Think step by step: first identify what is being asked, then locate the specific numbers or facts in the text.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Compare or process the extracted data logically based on the question's requirements (e.g., count, sum, compare sizes, etc.). Ensure your reasoning aligns with the problem structure.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Verify that all necessary information has been used correctly and that no critical detail was overlooked. Double-check for consistency between the question, passage, and your conclusion.</prompt>
    </node>
    
    <node id="5" type="output">
        <prompt>Provide a clear, concise final answer based on the processed logic from previous nodes. Do not include extra explanation unless required.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>