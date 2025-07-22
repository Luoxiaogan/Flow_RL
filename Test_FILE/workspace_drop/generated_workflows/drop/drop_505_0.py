# Workflow ID: drop_505_0
# Benchmark: drop
# Data Indices: [733, 876, 3898, 30, 2986]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract all relevant numerical data related to the question. Focus only on direct mentions of counts, scores, or yardages as needed.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted data is accurate and matches the context of the question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Perform necessary arithmetic operations (e.g., summing, comparing) based on the verified data.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Ensure the final answer aligns with the exact wording and intent of the question.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the final computed result in a concise format.</prompt>
  </node>

  <!-- Edges -->
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>