# Workflow ID: hotpotqa_119_0
# Benchmark: hotpotqa
# Data Indices: [1042, 759, 3858, 3521, 733]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for each question step by step.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Match extracted information to answer each question logically.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the correctness of each answer using contextual evidence.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answers as a structured list.</prompt>
    <depends_on>4</depends_on>
  </node>