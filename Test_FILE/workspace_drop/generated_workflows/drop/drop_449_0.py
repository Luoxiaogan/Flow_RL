# Workflow ID: drop_449_0
# Benchmark: drop
# Data Indices: [912, 2188, 620, 987]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities or events needed to answer it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage related to the question. Focus on specific details like names, scores, or actions mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Process the extracted data: count occurrences, calculate totals, or identify relationships between entities.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the processed result aligns with the question's requirements—ensure no misinterpretation of context or numbers.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the verified result from the previous step.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>