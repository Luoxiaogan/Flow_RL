# Workflow ID: drop_17_0
# Benchmark: drop
# Data Indices: [2162, 617, 1100, 2031, 501]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract the relevant numerical data from the passage that answers the question. Identify key phrases like 'how many', 'number of', or specific values mentioned.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the exact part of the passage that directly addresses the question. Look for sentences containing the answer or a clear reference to it.</instruction>
        <input>problem</input>
        <output>relevant_sentence</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Parse the extracted data to determine if it matches the required format (e.g., integer, count). If multiple numbers exist, isolate the one relevant to the question.</instruction>
        <input>extracted_data</input>
        <output>parsed_value</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Validate the parsed value against the context of the question to ensure correctness and avoid misinterpretation (e.g., check if it's a total, difference, or specific instance).</instruction>
        <input>parsed_value, relevant_sentence</input>
        <output>validated_answer</output>
    </node>
    
    <node id="6" type="output">
        <input>validated_answer</input>
    </node>
    
    <edge from="1" to="2" />
    <edge from="1" to="3" />
    <edge from="2" to="4" />
    <edge from="3" to="4" />
    <edge from="4" to="5" />
    <edge from="5" to="6" />