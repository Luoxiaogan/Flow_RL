# Workflow ID: hotpotqa_590_0
# Benchmark: hotpotqa
# Data Indices: [1483, 2658, 85, 1651]

<node id="1">
    <instruction>Identify the key elements in the question and context to determine the relevant information.</instruction>
    <output>Extracted key terms and entities from the problem and context.</output>
  </node>
  <node id="2">
    <instruction>Map each extracted term to its corresponding value or concept in the provided context.</instruction>
    <output>Established mappings between question components and contextual data.</output>
  </node>
  <node id="3">
    <instruction>Validate that the mapped values satisfy the conditions of the question, ensuring no ambiguity or misinterpretation.</instruction>
    <output>Confirmed correct alignment between question requirements and contextual facts.</output>
  </node>
  <node id="4">
    <instruction>Generate a concise answer based on validated mappings, ensuring it directly addresses the question without extraneous detail.</instruction>
    <output>Final answer derived from verified contextual evidence.</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>