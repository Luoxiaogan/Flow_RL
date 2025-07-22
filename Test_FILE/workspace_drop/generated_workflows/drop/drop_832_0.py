# Workflow ID: drop_832_0
# Benchmark: drop
# Data Indices: [3305, 3464, 2077, 1943]

<node id="1">
    <instruction>Understand the question and identify key elements such as the subject, action, and context.</instruction>
    <next>2</next>
  </node>
  <node id="2">
    <instruction>Extract relevant information from the passage that directly answers the question. Focus on specific events, people, or numbers mentioned.</instruction>
    <next>3</next>
  </node>
  <node id="3">
    <instruction>Verify that the extracted information matches the question's requirements—ensure it’s not a partial or misleading answer.</instruction>
    <next>4</next>
  </node>
  <node id="4">
    <instruction>Format the final answer clearly and concisely based on the verified information.</instruction>
    <next>5</next>
  </node>
  <node id="5">
    <instruction>Double-check for consistency with the passage and correctness of the logic used to arrive at the answer.</instruction>
    <next>end</next>
  </node>