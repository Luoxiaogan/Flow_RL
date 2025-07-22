# Workflow ID: drop_81_0
# Benchmark: drop
# Data Indices: [3757, 1433, 2863, 2081, 3828]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data related to the question. Focus on specific values (e.g., field goal distances, touchdown runs, etc.) mentioned in the passage.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Identify the maximum and minimum values among the extracted data points for comparison.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="agent">
    <prompt>Calculate the difference between the maximum and minimum values to answer the question.</prompt>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <prompt>Return the computed difference as the final answer.</prompt>
    <dependencies>4</dependencies>
  </node>