# Workflow ID: drop_724_0
# Benchmark: drop
# Data Indices: [3964, 3934, 3992, 1765]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Step-by-step reasoning: Identify all relevant events or actions related to the question. For example, if the question asks about touchdowns, locate all passing touchdowns mentioned in the passage.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Step-by-step reasoning: Filter only those events that occurred in the first half of the game (first two quarters). Exclude any touchdowns from the second half.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Step-by-step reasoning: Count the number of passing touchdowns identified in the first half. Ensure no rushing or other types of touchdowns are included.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final count as the answer to the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>