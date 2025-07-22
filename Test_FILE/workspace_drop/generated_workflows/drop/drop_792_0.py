# Workflow ID: drop_792_0
# Benchmark: drop
# Data Indices: [1166, 844, 1663, 1579]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Identify all values that directly answer the query.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Filter and validate the extracted values to ensure they correspond to the specific query. Discard any irrelevant or ambiguous entries.</instruction>
        <input>2</input>
        <output>filtered_values</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Summarize the filtered values into a final answer if multiple values are found, or return the single value if applicable.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <param name="answer" />
        <input>4</input>
    </node>