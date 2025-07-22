# Workflow ID: hotpotqa_533_0
# Benchmark: hotpotqa
# Data Indices: [885, 1452, 3857, 2729]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context: Identify the player who won Best Footballer in Asia 2015.</prompt>
    <output>Son Heung-min</output>
  </node>
  <node id="3" type="agent">
    <prompt>Find the birthdate of Son Heung-min from the context.</prompt>
    <output>8 July 1992</output>
  </node>
  <node id="4" type="output">
    <prompt>Return the birthdate of the player who won Best Footballer in Asia 2015.</prompt>
    <input>8 July 1992</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>