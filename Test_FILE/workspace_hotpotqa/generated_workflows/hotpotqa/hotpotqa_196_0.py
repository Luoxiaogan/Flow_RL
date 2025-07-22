# Workflow ID: hotpotqa_196_0
# Benchmark: hotpotqa
# Data Indices: [112, 3342, 1085, 717, 66]

<agent id="1" type="reasoning">
    <instruction>Step-by-step analysis of the question and context to identify key facts relevant to the answer.</instruction>
  </agent>
  <agent id="2" type="comparison">
    <instruction>Compare the relevant data points from the context to determine the correct answer based on the question.</instruction>
  </agent>
  <agent id="3" type="verification">
    <instruction>Verify the conclusion by cross-checking with the most reliable information in the context.</instruction>
  </agent>
  <agent id="4" type="output">
    <instruction>Generate the final, concise answer based on the verified result from the previous agents.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>