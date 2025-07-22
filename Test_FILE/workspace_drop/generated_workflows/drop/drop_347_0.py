# Workflow ID: drop_347_0
# Benchmark: drop
# Data Indices: [2636, 811, 740, 157, 3647]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question. Extract all numbers and their associated context.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter extracted data to only include values that directly answer the question. Discard irrelevant numbers or descriptions.</instruction>
    <input>extracted_data</input>
    <output>filtered_data</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply mathematical operations (e.g., subtraction, comparison) if needed to derive the final answer from filtered data.</instruction>
    <input>filtered_data</input>
    <output>result</output>
  </node>
  <node id="5" type="output">
    <input>result</input>
  </node>