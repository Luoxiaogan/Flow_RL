# Workflow ID: hotpotqa_140_0
# Benchmark: hotpotqa
# Data Indices: [1537, 3318, 2273, 1407]

<operator id="1">
    <instruction>Identify the key entities in the problem and their relationships. Break down the question into logical components.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>

  <operator id="2">
    <instruction>Extract relevant information from the context that directly answers the question. Focus only on facts tied to the main query.</instruction>
    <input>entity_analysis, context</input>
    <output>relevant_facts</output>
  </operator>

  <operator id="3">
    <instruction>Verify if the extracted facts are sufficient to answer the question. If not, identify missing links or clarify ambiguities.</instruction>
    <input>relevant_facts</input>
    <output>verification</output>
  </operator>

  <operator id="4">
    <instruction>Construct a concise and accurate response based on verified facts. Ensure no extraneous details are included.</instruction>
    <input>verification</input>
    <output>final_answer</output>
  </operator>

  <operator id="5">
    <instruction>Double-check all steps for consistency and correctness. Confirm that each operator’s output logically leads to the next.</instruction>
    <input>final_answer</input>
    <output>quality_assurance</output>
  </operator>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>