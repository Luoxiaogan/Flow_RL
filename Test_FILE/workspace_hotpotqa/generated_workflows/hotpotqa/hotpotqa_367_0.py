# Workflow ID: hotpotqa_367_0
# Benchmark: hotpotqa
# Data Indices: [3912, 2856, 2748, 1946]

<operator id="1">
    <instruction>Identify the key entities in the problem statement and determine the relationships between them.</instruction>
    <input>problem</input>
    <output>entity_list, relationship_map</output>
  </operator>
  <operator id="2">
    <instruction>Filter relevant context based on the entity list to extract only pertinent information.</instruction>
    <input>entity_list, relationship_map, context</input>
    <output>filtered_context</output>
  </operator>
  <operator id="3">
    <instruction>Parse the filtered context to locate the exact answer using logical deduction.</instruction>
    <input>filtered_context</input>
    <output>answer</output>
  </operator>
  <operator id="4">
    <instruction>Validate the answer by cross-referencing with multiple pieces of evidence in the filtered context.</instruction>
    <input>answer, filtered_context</input>
    <output>validated_answer</output>
  </operator>
  <operator id="5">
    <instruction>Format the final answer in a clear and concise manner for the user.</instruction>
    <input>validated_answer</input>
    <output>final_output</output>
  </operator>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>
  <link from="4" to="5"/>