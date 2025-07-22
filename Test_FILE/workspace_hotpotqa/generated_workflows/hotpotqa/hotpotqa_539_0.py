# Workflow ID: hotpotqa_539_0
# Benchmark: hotpotqa
# Data Indices: [3554, 2017, 3059, 2736]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem statement. Break down the question to isolate the core information needed for the answer.</instruction>
    <input>problem</input>
    <output>parsed_question</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant context from the provided text that directly addresses the parsed question. Focus only on the most pertinent details.</instruction>
    <input>parsed_question, context</input>
    <output>relevant_context</output>
  </operator>
  <operator id="2">
    <instruction>Verify the extracted context against the question to ensure it provides a clear and unambiguous answer.</instruction>
    <input>relevant_context, parsed_question</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Format the validated answer into a concise, precise response that directly answers the original question.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>