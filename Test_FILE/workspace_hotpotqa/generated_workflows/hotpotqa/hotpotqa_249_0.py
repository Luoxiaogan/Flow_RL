# Workflow ID: hotpotqa_249_0
# Benchmark: hotpotqa
# Data Indices: [1316, 2862, 1821, 3600, 3813]

<operator id="1" type="agent">
    <instruction>Think step by step to analyze the question and context. Identify the key entities and relationships that directly answer the question.</instruction>
    <input>problem</input>
    <output>step_by_step_analysis</output>
  </operator>

  <operator id="2" type="agent">
    <instruction>Extract relevant facts from the context that pertain to the entities mentioned in the question. Focus only on information that supports or contradicts the claim.</instruction>
    <input>step_by_step_analysis</input>
    <output>extracted_facts</output>
  </operator>

  <operator id="3" type="agent">
    <instruction>Determine whether the statement in the question is true, false, or cannot be determined based on the extracted facts. Provide a clear justification using logical reasoning.</instruction>
    <input>extracted_facts</input>
    <output>final_answer</output>
  </operator>

  <operator id="4" type="agent">
    <instruction>Verify the final answer by cross-checking with all available context to ensure no critical detail was missed.</instruction>
    <input>final_answer</input>
    <output>verified_answer</output>
  </operator>

  <operator id="5" type="agent">
    <instruction>Format the verified answer into a concise, structured response suitable for direct output. Ensure clarity and precision.</instruction>
    <input>verified_answer</input>
    <output>formatted_output</output>
  </operator>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>