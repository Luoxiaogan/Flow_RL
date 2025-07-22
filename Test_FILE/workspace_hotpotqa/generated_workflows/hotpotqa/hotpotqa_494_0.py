# Workflow ID: hotpotqa_494_0
# Benchmark: hotpotqa
# Data Indices: [1717, 3150, 3691, 1853]

<node id="1" type="input">
        <description>Receive problem context and question</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify key entities and relevant data in the context that answer the question. Think step by step: First, locate the genus or subject mentioned in the question. Second, find the species count or defining attribute in the context. Third, compare values if needed.</instruction>
        <output>Extracted relevant data point</output>
    </node>
    <node id="3" type="agent">
        <instruction>Verify extracted data against the question's requirement. If comparing two entities (e.g., Solanum vs Coelia), ensure both are fully evaluated. Think step by step: First, confirm which entity is being compared. Second, check the numeric value for each. Third, determine the correct answer based on comparison.</instruction>
        <output>Confirmed answer</output>
    </node>
    <node id="4" type="output">
        <description>Return the final answer to the question</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>