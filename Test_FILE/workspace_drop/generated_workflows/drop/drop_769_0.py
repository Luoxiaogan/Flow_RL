# Workflow ID: drop_769_0
# Benchmark: drop
# Data Indices: [1446, 443, 3045, 2819]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical data from the passage relevant to the question. Identify all explicit values and their contexts.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific time frame or event mentioned in the question and locate it within the passage context.</instruction>
    <input>1</input>
    <output>contextual_info</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply logical reasoning using extracted data and contextual info to compute the answer step by step.</instruction>
    <input>2,3</input>
    <output>reasoned_answer</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the computed answer against known facts in the passage for consistency and accuracy.</instruction>
    <input>1,4</input>
    <output>verified_answer</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>