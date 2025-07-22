# Workflow ID: hotpotqa_94_0
# Benchmark: hotpotqa
# Data Indices: [128, 3447, 274, 2047, 1679]

<operator id="0" type="agent">
    <instruction>Think step by step to identify the key elements in the problem and determine the correct answer.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract relevant facts from the context that directly relate to the question being asked.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Verify if the extracted facts are sufficient to answer the question or if further reasoning is needed.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Use logical deduction to connect the relevant facts and arrive at a definitive conclusion.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Check for consistency between the conclusion and all provided contextual information.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Ensure the final answer aligns with the question's requirements without introducing unsupported claims.</instruction>
  </operator>
  <operator id="6" type="agent">
    <instruction>Output only the final, verified answer as a concise response.</instruction>
  </operator>
  <connection from="0" to="1"/>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>
  <connection from="5" to="6"/>