# Workflow ID: drop_855_0
# Benchmark: drop
# Data Indices: [937, 2691, 2247, 3641, 2949]

<agent id="1" type="extract">
    <instruction>Identify the key numerical data points related to the question from the passage.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>From the extracted data, filter out values that meet the condition specified in the question.</instruction>
  </agent>
  <agent id="3" type="calculate">
    <instruction>Perform the necessary calculation based on the filtered data to answer the question.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify that the calculated result aligns with the context of the question and passage.</instruction>
  </agent>
  <agent id="5" type="output">
    <instruction>Return the final answer as a single numeric value or percentage, ensuring it matches the question's requirement.</instruction>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>