# Workflow ID: hotpotqa_459_0
# Benchmark: hotpotqa
# Data Indices: [1905, 1444, 2494, 987, 473]

<operator id="0" type="agent">
    <instruction>Think step by step to identify the key elements of the problem and determine the correct answer based on logical reasoning.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract relevant details from the context that directly relate to the question. Focus only on information that supports or contradicts potential answers.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Compare the extracted details with known facts or patterns in the context to narrow down possible solutions.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Validate each candidate solution against all provided context clues to ensure accuracy and avoid false positives.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Combine validated results from previous steps to produce a final, coherent answer.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Review the final answer for clarity, correctness, and completeness—ensure it fully addresses the original question.</instruction>
  </operator>
  <operator id="6" type="agent">
    <instruction>Output only the final answer without any additional explanation or formatting.</instruction>
  </operator>
  <connection from="0" to="1"/>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>
  <connection from="5" to="6"/>