# Workflow ID: hotpotqa_277_0
# Benchmark: hotpotqa
# Data Indices: [3384, 2381, 448, 1003, 50]

<node id="start" type="input">
    <prompt>Begin processing the problem by identifying key entities and relationships in the context.</prompt>
  </node>
  
  <node id="analyze_entities" type="agent">
    <prompt>Extract and categorize all named entities (people, bands, albums, locations, etc.) from the context. Focus on those relevant to answering the question.</prompt>
    <dependencies>start</dependencies>
  </node>
  
  <node id="map_relations" type="agent">
    <prompt>Map the relationships between extracted entities—e.g., band formation dates, album themes, personal connections—to determine which entity satisfies the query condition.</prompt>
    <dependencies>analyze_entities</dependencies>
  </node>
  
  <node id="compare_values" type="agent">
    <prompt>Compare the relevant values (e.g., years of activity) for each candidate entity to determine which one meets the criteria in the question.</prompt>
    <dependencies>map_relations</dependencies>
  </node>
  
  <node id="validate_solution" type="agent">
    <prompt>Verify that the selected answer aligns with the facts in the context and logically resolves the question without contradictions.</prompt>
    <dependencies>compare_values</dependencies>
  </node>
  
  <node id="output" type="output">
    <prompt>Return the final answer as a concise string based on the validated solution.</prompt>
    <dependencies>validate_solution</dependencies>
  </node>