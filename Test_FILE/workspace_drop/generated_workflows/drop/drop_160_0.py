# Workflow ID: drop_160_0
# Benchmark: drop
# Data Indices: [786, 897, 3156, 3227]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific numerical or comparative data mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted values or categories to determine which option satisfies the condition in the question (e.g., "more surface area", "longest pass", etc.).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the comparison logic by cross-checking with the passage to ensure no misinterpretation occurred.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified comparison.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>