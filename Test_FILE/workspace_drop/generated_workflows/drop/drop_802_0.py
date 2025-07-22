# Workflow ID: drop_802_0
# Benchmark: drop
# Data Indices: [1573, 2100, 3094, 3126, 3638]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage related to the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Process the extracted data to find the answer based on the question's requirement.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Validate the result by cross-checking with other parts of the passage if necessary.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in the required format.</prompt>
    <depends_on>4</depends_on>
  </node>