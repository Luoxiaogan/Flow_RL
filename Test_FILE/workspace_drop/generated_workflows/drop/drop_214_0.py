# Workflow ID: drop_214_0
# Benchmark: drop
# Data Indices: [895, 3843, 3377, 2885]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage. Identify all numbers mentioned that could be part of a calculation.</instruction>
        <input>1</input>
        <output>extracted_numbers</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question. Determine which numbers are directly related to the query and discard irrelevant ones.</instruction>
        <input>2</input>
        <output>relevant_values</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic operation (e.g., subtraction, division) based on the relevant values to derive the final answer.</instruction>
        <input>3</input>
        <output>result</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>