# Workflow ID: hotpotqa_410_0
# Benchmark: hotpotqa
# Data Indices: [3959, 3170, 2307, 3493, 1151]

<start/>
  <agent id="1" type="extract">
    <instruction>Extract the key entities and relationships from the context relevant to the question.</instruction>
  </agent>
  <agent id="2" type="reason">
    <instruction>Use logical reasoning to connect extracted entities and identify the correct answer based on the relationships.</instruction>
  </agent>
  <agent id="3" type="validate">
    <instruction>Verify the consistency of the answer with all provided contextual information to avoid contradictions.</instruction>
  </agent>
  <agent id="4" type="output">
    <instruction>Format the final answer clearly, ensuring it directly addresses the question without extra details.</instruction>
  </agent>
  <end/>
  <edge from="start" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>