# Workflow ID: drop_702_0
# Benchmark: drop
# Data Indices: [2666, 2233, 3590, 2104, 1364]

<node id="1" type="input">
        <prompt>Understand the question and extract relevant information from the passage.</prompt>
    </node>
    
    <node id="2" type="process">
        <prompt>Identify key numerical data points related to the question (e.g., percentages, counts, scores).</prompt>
    </node>
    
    <node id="3" type="process">
        <prompt>Apply mathematical operations or logical reasoning based on the extracted data.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Generate the final answer by synthesizing results from previous steps.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>