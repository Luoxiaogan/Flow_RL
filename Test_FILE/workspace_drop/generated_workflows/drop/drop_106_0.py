# Workflow ID: drop_106_0
# Benchmark: drop
# Data Indices: [3029, 720, 473, 131]

<node id="1" type="input">
    <prompt>Understand the question and identify the key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage that directly answers the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted number matches the context of the question exactly.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Ensure no extra or irrelevant numbers are included in the final answer.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the correct numerical answer based on the verified extraction.</prompt>
    <depends_on>4</depends_on>
  </node>