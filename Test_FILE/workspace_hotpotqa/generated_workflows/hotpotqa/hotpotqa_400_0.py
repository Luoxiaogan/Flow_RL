# Workflow ID: hotpotqa_400_0
# Benchmark: hotpotqa
# Data Indices: [637, 943, 3779, 2461]

<node id="1" type="input">
    <description>Receive problem context and question</description>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify key entities in the question and context. Focus on geographical, cultural, or historical terms that match known regions or locations.</instruction>
    <output>Extracted entities: Liverpool, northern/southern England</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Based on extracted entities, locate Liverpool in England using geographic knowledge from the context. Consider regional divisions such as Lancashire or modern administrative boundaries.</instruction>
    <output>Liverpool is in South Lancashire, which is part of northern England</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Verify the classification of Liverpool by cross-referencing with other context clues (e.g., "South Lancashire" mentioned in relation to Manchester and Liverpool).</instruction>
    <output>Confirmed: Liverpool is in northern England</output>
  </node>
  
  <node id="5" type="output">
    <instruction>Return the final answer based on verified location.</instruction>
    <output>northern England</output>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>