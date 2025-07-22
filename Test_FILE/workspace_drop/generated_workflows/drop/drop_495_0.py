# Workflow ID: drop_495_0
# Benchmark: drop
# Data Indices: [3663, 3078, 3096, 1422]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points relevant to the question. Extract all values that represent counts, measurements, or comparisons mentioned in the passage.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>For each numerical value extracted, determine its relevance to the specific question asked. Filter out any irrelevant numbers and retain only those directly tied to the query.</instruction>
        <input>2</input>
        <output>filtered_data</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic or logical comparison based on the filtered data to answer the question step by step.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>