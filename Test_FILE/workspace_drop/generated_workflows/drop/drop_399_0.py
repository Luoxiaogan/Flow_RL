# Workflow ID: drop_399_0
# Benchmark: drop
# Data Indices: [3100, 78, 1633, 288, 713]

<node id="1" type="input">
        <prompt>Understand the question and identify key information needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant data from the passage that directly answers the question. Think step by step: first locate the key terms, then find the exact value or statement related to the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted data is sufficient to answer the question. If not, identify what additional information might be needed and check for implicit connections in the passage.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Perform any necessary comparison, calculation, or logical reasoning using the extracted data to derive the final answer. Ensure each step is clearly justified.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on the previous steps. Double-check that it directly addresses the original question without ambiguity.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>