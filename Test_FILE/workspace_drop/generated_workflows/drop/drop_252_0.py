# Workflow ID: drop_252_0
# Benchmark: drop
# Data Indices: [3823, 2385, 3789, 2877]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question. Identify all values that pertain to the specific query, such as field goals, yards, or other measurable quantities.</instruction>
        <input>problem</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>Filter and isolate only the values directly answering the question. For example, if the question asks about field goals in a specific period, focus on those numbers from the extracted data.</instruction>
        <input>extracted_values</input>
        <output>filtered_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Sum up or process the filtered values as required by the question—e.g., total yards from multiple passes or total field goals made.</instruction>
        <input>filtered_values</input>
        <output>processed_result</output>
    </node>
    <node id="5" type="output">
        <param>final_answer</param>
        <input>processed_result</input>
    </node>