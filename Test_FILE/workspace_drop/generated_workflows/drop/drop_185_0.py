# Workflow ID: drop_185_0
# Benchmark: drop
# Data Indices: [3489, 547, 3780, 1616]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant numerical data from the passage that directly relates to the question.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Perform necessary arithmetic or logical operations using the extracted data to derive the answer.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="output">
        <prompt>Return the final answer based on the computed result from the previous step.</prompt>
        <dependencies>3</dependencies>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>