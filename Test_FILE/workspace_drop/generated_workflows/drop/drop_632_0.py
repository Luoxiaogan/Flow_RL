# Workflow ID: drop_632_0
# Benchmark: drop
# Data Indices: [46, 2513, 2434, 32, 3379]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the mathematical operation required to solve the problem based on the question.</instruction>
    <input>2</input>
    <output>operation</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform the calculation using the extracted data and identified operation.</instruction>
    <input>2,3</input>
    <output>result</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the result by cross-checking with the original passage and ensure it answers the question directly.</instruction>
    <input>1,4</input>
    <output>verification</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>