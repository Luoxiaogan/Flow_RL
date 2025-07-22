# Workflow ID: drop_628_0
# Benchmark: drop
# Data Indices: [418, 3230, 301, 903]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or metrics needed for comparison.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage that directly answers the question. Focus on specific values or events mentioned.</prompt>
    <dependency>1</dependency>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted values step by step to determine which option is correct based on evidence.</prompt>
    <dependency>2</dependency>
  </node>
  <node id="4" type="output">
    <prompt>Provide a clear, concise answer based on the comparison. Ensure it directly addresses the original question.</prompt>
    <dependency>3</dependency>
  </node>