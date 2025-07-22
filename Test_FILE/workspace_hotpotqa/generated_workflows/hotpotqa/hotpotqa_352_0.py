# Workflow ID: hotpotqa_352_0
# Benchmark: hotpotqa
# Data Indices: [2257, 225, 2660, 2628]

<operator id="0">
    <instruction>Extract key entities from the input context that relate to the question.</instruction>
    <input>problem</input>
    <output>entities</output>
  </operator>
  <operator id="1">
    <instruction>Identify the relevant information in the context that directly answers the question.</instruction>
    <input>entities, problem</input>
    <output>answer_clue</output>
  </operator>
  <operator id="2">
    <instruction>Validate the answer clue by cross-referencing with other parts of the context to ensure accuracy.</instruction>
    <input>answer_clue, problem</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Format the final answer based on the validated result, ensuring clarity and correctness.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>