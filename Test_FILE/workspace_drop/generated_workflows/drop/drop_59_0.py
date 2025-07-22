# Workflow ID: drop_59_0
# Benchmark: drop
# Data Indices: [3025, 2891, 2637, 3664]

<node id="1" type="input">
    <prompt>Understand the problem and extract relevant information from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the key elements needed to solve the question. For example, in Problem 1, locate all touchdowns and the player's name.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Filter for specific conditions (e.g., only touchdowns by rookies in Problem 3).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Calculate or determine the final answer based on filtered data (e.g., count touchdowns or compute point difference).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer clearly and concisely.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>