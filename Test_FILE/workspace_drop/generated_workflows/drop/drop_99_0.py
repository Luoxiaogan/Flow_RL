# Workflow ID: drop_99_0
# Benchmark: drop
# Data Indices: [2963, 423, 2851, 864, 1690]

<node id="1" type="input">
    <prompt>Understand the question and identify key temporal or numerical relationships.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the chronological sequence or numerical value required by the question. Think step by step to determine which event occurred first or what number is being asked for.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Extract relevant data from the passage that directly answers the question. Focus only on facts that support the answer—avoid unnecessary details.</prompt>
  </node>
  <node id="4" type="operator">
    <prompt>Compare events or values based on extracted data. If it's a timeline, order events chronologically; if it's a count, compute the exact number.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Verify that the derived answer matches the question’s requirements exactly—no extra information, no missing parts.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the final answer as a single, clear result based on all prior steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>