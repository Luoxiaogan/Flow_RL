# Workflow ID: drop_585_0
# Benchmark: drop
# Data Indices: [2407, 3363, 2871, 3454, 1087]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant statistics in the passage related to the question. For example, if the question asks about touchdowns, find all instances of touchdown passes or runs. If it's about field goals, locate each field goal and its distance.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Filter and categorize the data based on the question. For instance, separate passing touchdowns from rushing touchdowns, or group field goals by distance ranges (e.g., 25–50 yards).</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Count the relevant entries. If the question is about how many, tally the filtered items—like total passing touchdowns or field goals within a specific yard range.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Validate your count against the passage. Ensure no missed references and that the logic aligns with the question’s focus (e.g., only first-half stats for Q4).</instruction>
  </node>
  <node id="6" type="output">
    <description>Return the final numerical answer based on the validated count.</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>