# Workflow ID: hotpotqa_154_0
# Benchmark: hotpotqa
# Data Indices: [3709, 3457, 3004, 2611]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the context for each question. Focus on one question at a time, step by step.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Match the extracted information to the correct answer for each question using logical reasoning.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that each answer is consistent with the context provided and cross-check for any contradictions.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answers for all questions in a structured format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>