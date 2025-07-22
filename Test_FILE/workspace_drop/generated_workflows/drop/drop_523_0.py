# Workflow ID: drop_523_0
# Benchmark: drop
# Data Indices: [3092, 367, 2249, 2365, 2741]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question. Identify all yardages mentioned in the context of touchdowns or scoring plays.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Filter and sort the extracted yardages to determine the second shortest touchdown pass. Consider only touchdown passes, not field goals or runs.</instruction>
        <input>2</input>
        <output>sorted_passes</output>
    </node>
    <node id="4" type="agent">
        <instruction>Identify the second smallest value from the sorted list of touchdown pass yardages. This is the answer to the question.</instruction>
        <input>3</input>
        <output>second_shortest</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>