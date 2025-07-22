# Workflow ID: drop_766_0
# Benchmark: drop
# Data Indices: [2615, 3648, 2062, 3723]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities and relationships.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage related to the question. Focus on chronological or comparative details as needed.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Determine the sequence or magnitude based on extracted data—e.g., years, population counts, or event order.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that all necessary steps are completed and no critical detail is missed in the reasoning chain.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer based on the logical flow of the previous agents' outputs.</prompt>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>