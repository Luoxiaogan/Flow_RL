# Workflow ID: drop_695_0
# Benchmark: drop
# Data Indices: [718, 3310, 202, 2795]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or quantities to extract.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage related to the question. Focus on specific details like names, numbers, or events.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted data answers the question directly. If multiple pieces of information are needed, ensure they are all included.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any indirect clues or contextual hints that might affect the interpretation of the answer.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on validated extraction and reasoning. Ensure clarity and correctness.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>