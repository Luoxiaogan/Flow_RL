# Workflow ID: hotpotqa_379_0
# Benchmark: hotpotqa
# Data Indices: [2714, 541, 2806, 157, 28]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify relevant context that directly answers the question. Focus on specific details like names, dates, or relationships.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted information against all provided context to ensure accuracy and avoid false positives.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any indirect references or clues in the context that may support the answer.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Combine findings from previous nodes into a coherent answer using logical reasoning.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the final answer based on verified evidence.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>