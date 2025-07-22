# Workflow ID: drop_631_0
# Benchmark: drop
# Data Indices: [934, 3010, 1504, 3907, 3048]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data points in the passage related to the question. Focus on specific events, counts, or percentages mentioned.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract and isolate the relevant information from the passage that directly answers the question. Ignore any extraneous details.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the extracted information matches the exact requirement of the question. If multiple values are present, determine which one is correct based on context.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Format the final answer clearly and concisely, ensuring it directly responds to the question without additional explanation unless necessary.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <param name="answer">5</param>
    <input>5</input>
  </node>