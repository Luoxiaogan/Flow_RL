# Workflow ID: hotpotqa_595_0
# Benchmark: hotpotqa
# Data Indices: [3299, 212, 1979, 262, 3173]

<node id="1">
    <instruction>Identify the key elements in the question: the singer of "Confident" and the Disney Channel movie they starred in.</instruction>
  </node>
  <node id="2">
    <instruction>From the context, locate which artist is associated with the song "Confident".</instruction>
  </node>
  <node id="3">
    <instruction>Determine the Disney Channel movie this artist starred in based on the context provided.</instruction>
  </node>
  <node id="4">
    <instruction>Verify that the identified movie is indeed a Disney Channel original movie and matches the actor's filmography.</instruction>
  </node>
  <node id="5">
    <instruction>Return the name of the Disney Channel movie as the final answer.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>