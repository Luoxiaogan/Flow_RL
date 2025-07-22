# Workflow ID: drop_246_0
# Benchmark: drop
# Data Indices: [2710, 1945, 3527, 1457]

<node id="1" type="input">
    <prompt>Extract the relevant numerical value from the passage based on the question.</prompt>
  </node>
  <node id="2" type="operator">
    <prompt>Identify the key event and corresponding yardage mentioned in the passage that answers the question.</prompt>
    <dependency>1</dependency>
  </node>
  <node id="3" type="operator">
    <prompt>Verify that the extracted value matches the context of the question asked.</prompt>
    <dependency>2</dependency>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer as a single number, derived from the verified value.</prompt>
    <dependency>3</dependency>
  </node>