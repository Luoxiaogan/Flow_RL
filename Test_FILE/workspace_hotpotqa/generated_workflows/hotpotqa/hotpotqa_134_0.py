# Workflow ID: hotpotqa_134_0
# Benchmark: hotpotqa
# Data Indices: [1320, 1185, 1760, 1345]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question. Focus on named entities, dates, and relationships.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Map the extracted entities to known facts or categories (e.g., religion, historical event, artist).</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Identify how the entities interact or influence each other based on the context.</prompt>
  </node>
  
  <node id="5" type="agent">
    <prompt>Determine the final answer by synthesizing the mapped and relational data.</prompt>
  </node>
  
  <node id="6" type="output">
    <prompt>Return the correct answer based on the synthesized result.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>