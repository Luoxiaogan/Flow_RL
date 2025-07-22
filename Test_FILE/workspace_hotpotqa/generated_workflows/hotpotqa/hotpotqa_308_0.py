# Workflow ID: hotpotqa_308_0
# Benchmark: hotpotqa
# Data Indices: [3344, 560, 2419, 3198]

<operator id="0" type="agent">
    <instruction>Identify the key entities and relationships in the problem statement. Break down the question into smaller components to isolate the required information.</instruction>
    <input>problem</input>
    <output>structured_entities</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract relevant facts from the context that directly answer the question. Focus only on data tied to the identified entities.</instruction>
    <input>structured_entities, context</input>
    <output>relevant_facts</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Validate the relevance and accuracy of each extracted fact. Eliminate any ambiguous or irrelevant information that does not contribute to the final answer.</instruction>
    <input>relevant_facts</input>
    <output>validated_facts</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Construct a logical sequence based on validated facts to derive the correct answer step by step.</instruction>
    <input>validated_facts</input>
    <output>reasoning_chain</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Verify the reasoning chain against known facts and ensure consistency with the provided context.</instruction>
    <input>reasoning_chain, context</input>
    <output>final_answer</output>
  </operator>
  <operator id="5" type="agent">
    <instruction>Check for completeness: ensure all steps are covered, no missing links, and the answer fully addresses the original question.</instruction>
    <input>final_answer</input>
    <output>verified_answer</output>
  </operator>
  <edge from="0" to="1" />
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />