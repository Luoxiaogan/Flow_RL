# Workflow ID: hotpotqa_213_0
# Benchmark: hotpotqa
# Data Indices: [317, 1766, 1305, 1704, 723]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for each question. Focus on one entity at a time to avoid confusion.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare and contrast the extracted information to determine the correct answer for each question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that each answer is directly supported by the context provided, ensuring no assumptions are made.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answers in a structured format: [answer1, answer2, answer3, answer4, answer5].</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>