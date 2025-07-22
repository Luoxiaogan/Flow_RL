# Workflow ID: hotpotqa_5_0
# Benchmark: hotpotqa
# Data Indices: [2082, 1556, 598, 1562, 2085]

<agent id="1" type="extract">
    <instruction>Extract the key entities and relationships from the context relevant to the question.</instruction>
  </agent>
  <agent id="2" type="reason">
    <instruction>Reason step-by-step: Identify the direct answer by connecting the extracted entities. If ambiguous, list possible candidates.</instruction>
  </agent>
  <agent id="3" type="verify">
    <instruction>Verify the candidate answer against all context clues. Eliminate incorrect options if multiple exist.</instruction>
  </agent>
  <agent id="4" type="resolve">
    <instruction>If verification yields uncertainty, resolve by cross-referencing with external knowledge or logical deduction based on context.</instruction>
  </agent>
  <agent id="5" type="output">
    <instruction>Finalize the answer based on resolved evidence. Ensure it directly addresses the question.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>