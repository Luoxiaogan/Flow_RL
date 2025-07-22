# Workflow ID: drop_155_0
# Benchmark: drop
# Data Indices: [1924, 1597, 503, 3974]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the key metric or value being asked in the question from the extracted data.</instruction>
    <input>2</input>
    <output>key_metric</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform any necessary calculation (e.g., subtraction, percentage, etc.) to derive the final answer.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>result</output>
  </node>