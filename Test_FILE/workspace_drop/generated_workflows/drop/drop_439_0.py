# Workflow ID: drop_439_0
# Benchmark: drop
# Data Indices: [3853, 2728, 1553, 2483, 10]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Focus only on the values directly related to the query.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Process the extracted data to compute the required answer. If multiple values exist, determine which one is relevant (e.g., longest, total count, percentage).</instruction>
        <input>extracted_data</input>
        <output>processed_answer</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Validate the computed answer against the original context to ensure correctness and relevance to the question.</instruction>
        <input>processed_answer, problem</input>
        <output>validated_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>validated_answer</input>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>