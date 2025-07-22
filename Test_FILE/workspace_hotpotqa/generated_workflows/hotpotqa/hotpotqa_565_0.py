# Workflow ID: hotpotqa_565_0
# Benchmark: hotpotqa
# Data Indices: [309, 3367, 942, 1473, 3155]

<node id="1" type="input">
    <description>Receive problem context and question</description>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract key entities and dates from the context relevant to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  
  <node id="3" type="agent">
    <instruction>Match extracted entities with known facts in the context (e.g., actors, films, networks, or events).</instruction>
    <depends_on>2</depends_on>
  </node>
  
  <node id="4" type="agent">
    <instruction>Validate potential answers by checking consistency with temporal or categorical constraints (e.g., date ranges, roles, or affiliations).</instruction>
    <depends_on>3</depends_on>
  </node>
  
  <node id="5" type="agent">
    <instruction>Refine answer by eliminating duplicates or ambiguous matches using cross-references in the context.</instruction>
    <depends_on>4</depends_on>
  </node>
  
  <node id="6" type="output">
    <instruction>Return the final, most accurate answer based on all prior steps.</instruction>
    <depends_on>5</depends_on>
  </node>