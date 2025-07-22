# Workflow ID: drop_85_0
# Benchmark: drop
# Data Indices: [3790, 2526, 101, 3392]

<node id="start" type="input"/>
  <node id="step1" type="process">
    <instruction>Identify the relevant values from the passage for the calculation.</instruction>
  </node>
  <node id="step2" type="calculate">
    <instruction>Calculate the difference between the two percentages: (percentage aged 14 and over) - (percentage aged 60 and over).</instruction>
  </node>
  <node id="step3" type="format">
    <instruction>Express the difference as a percentage increase relative to the group aged 60 and over.</instruction>
  </node>
  <node id="end" type="output"/>
  <edge from="start" to="step1"/>
  <edge from="step1" to="step2"/>
  <edge from="step2" to="step3"/>
  <edge from="step3" to="end"/>