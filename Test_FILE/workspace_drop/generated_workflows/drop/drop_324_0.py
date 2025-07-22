# Workflow ID: drop_324_0
# Benchmark: drop
# Data Indices: [1034, 29, 2237, 810, 3466]

<start>
    <task>Extract relevant information from input</task>
    <next>Identify problem type and required calculation</next>
  </start>

  <node id="1">
    <task>Analyze question to determine what needs to be calculated</task>
    <next>Retrieve necessary data from passage</next>
  </node>

  <node id="2">
    <task>Locate and extract numerical values or events related to the question</task>
    <next>Validate extracted data for correctness</next>
  </node>

  <node id="3">
    <task>Perform arithmetic or logical operations based on the question</task>
    <next>Ensure all steps are accounted for in the solution</next>
  </node>

  <node id="4">
    <task>Verify that the answer matches the question's requirement</task>
    <next>Format the final output correctly</next>
  </node>

  <end>
    <task>Return the computed result</task>
  </end>

  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>