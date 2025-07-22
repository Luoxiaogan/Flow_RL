# Workflow ID: hotpotqa_512_0
# Benchmark: hotpotqa
# Data Indices: [860, 2250, 864, 3993, 1891]

<start/>
  <operator id="1">
    <instruction>Identify the key entities in the question and their relationships.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>
  <operator id="2">
    <instruction>Extract relevant context information that directly answers the question.</instruction>
    <input>entity_analysis, context</input>
    <output>retrieved_info</output>
  </operator>
  <operator id="3">
    <instruction>Validate the retrieved information against known facts to ensure accuracy.</instruction>
    <input>retrieved_info</input>
    <output>validated_info</output>
  </operator>
  <operator id="4">
    <instruction>Construct a clear and concise answer based on validated information.</instruction>
    <input>validated_info</input>
    <output>final_answer</output>
  </operator>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>