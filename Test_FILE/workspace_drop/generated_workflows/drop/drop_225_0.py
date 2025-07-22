# Workflow ID: drop_225_0
# Benchmark: drop
# Data Indices: [3906, 354, 359, 3901, 2930]

<start/>
  <agent id="1" type="extract">
    <instruction>Extract all relevant numerical data from the passage related to the question.</instruction>
  </agent>
  <agent id="2" type="calculate">
    <instruction>Perform necessary calculations using the extracted data to answer the question step by step.</instruction>
  </agent>
  <agent id="3" type="validate">
    <instruction>Verify the calculation against the passage to ensure accuracy and logical consistency.</instruction>
  </agent>
  <agent id="4" type="format">
    <instruction>Format the final answer clearly and concisely based on validated result.</instruction>
  </agent>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>