# Workflow ID: drop_426_0
# Benchmark: drop
# Data Indices: [3474, 1652, 3002, 2287, 2292]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify and isolate the specific value or values needed to answer the question, ensuring no irrelevant data is included.</instruction>
    <input>2</input>
    <output>filtered_value</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the filtered value matches the exact requirement of the question (e.g., length, count, score).</instruction>
    <input>3</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>