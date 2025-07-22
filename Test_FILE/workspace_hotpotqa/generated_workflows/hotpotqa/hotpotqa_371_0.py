# Workflow ID: hotpotqa_371_0
# Benchmark: hotpotqa
# Data Indices: [1481, 2909, 3576, 1289]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities.</prompt>
    <depends_on>1</depends_on>
  </node>
  
  <node id="3" type="agent">
    <prompt>Verify if the entities match the criteria in the question (e.g., band, town, person).</prompt>
    <depends_on>2</depends_on>
  </node>
  
  <node id="4" type="agent">
    <prompt>Check for any indirect connections or contextual clues that support the answer.</prompt>
    <depends_on>3</depends_on>
  </node>
  
  <node id="5" type="agent">
    <prompt>Formulate a clear, step-by-step reasoning path based on verified data.</prompt>
    <depends_on>4</depends_on>
  </node>
  
  <node id="6" type="output">
    <prompt>Return the final answer derived from the reasoning chain.</prompt>
    <depends_on>5</depends_on>
  </node>