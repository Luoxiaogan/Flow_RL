# Workflow ID: hotpotqa_406_0
# Benchmark: hotpotqa
# Data Indices: [1327, 3760, 1867, 3617]

<node id="1">
    <instruction>Identify the key entities in the problem and their relationships.</instruction>
    <output>Extract relevant facts, such as names, roles, and connections between entities.</output>
  </node>
  <node id="2">
    <instruction>Map each entity to its known attributes using contextual clues.</instruction>
    <output>Link entities (e.g., people, places, works) to their associated properties or categories.</output>
  </node>
  <node id="3">
    <instruction>Apply logical reasoning to eliminate incorrect options based on constraints.</instruction>
    <output>Filter out possibilities that contradict the given context or question.</output>
  </node>
  <node id="4">
    <instruction>Verify consistency of the remaining candidate answer with all provided information.</instruction>
    <output>Ensure the selected answer aligns with every piece of supporting evidence.</output>
  </node>
  <node id="5">
    <instruction>Generate final output by synthesizing all verified results.</instruction>
    <output>Return the correct answer based on the refined chain of reasoning.</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>