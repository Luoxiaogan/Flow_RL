# Workflow ID: drop_887_0
# Benchmark: drop
# Data Indices: [3321, 2850, 3708, 900]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical information in the passage relevant to the question. Focus on specific years, durations, or counts mentioned.</instruction>
        <input>1</input>
        <output>key_info</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract the exact value or range that answers the question based on the key information. Ensure it matches the question's requirement (e.g., duration, count, year).</instruction>
        <input>2</input>
        <output>answer_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the extracted value by cross-checking with the passage for consistency and accuracy. If inconsistent, re-evaluate step-by-step.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>