# Workflow ID: drop_304_0
# Benchmark: drop
# Data Indices: [1978, 2706, 1483, 3201, 2372]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    <node id="2" type="agent">
        <instruction>Extract all relevant numerical data from the passage related to the question. Identify key players, scores, and yardages mentioned.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific event or play that answers the question. Locate the relevant player(s) and yardage for the comparison or count requested.</instruction>
        <input>extracted_data</input>
        <output>relevant_play</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the required calculation based on the identified yardages or counts. If comparing, subtract the smaller value from the larger one. If counting, tally the specified events.</instruction>
        <input>relevant_play</input>
        <output>result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the result by cross-referencing with the original passage to ensure accuracy of the extracted data and calculation.</instruction>
        <input>result, problem</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <input>final_answer</input>
    </node>