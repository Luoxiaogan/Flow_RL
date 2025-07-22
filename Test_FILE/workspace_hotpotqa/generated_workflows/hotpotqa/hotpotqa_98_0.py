# Workflow ID: hotpotqa_98_0
# Benchmark: hotpotqa
# Data Indices: [1142, 3550, 911, 1957, 3125]

<operator id="1" type="agent">
    <instruction>Identify the key entities and their relationships in the problem context. Focus on extracting relevant dates, names, and roles that directly answer the question.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>For each key entity, determine its relevance to the question. Filter out any information that does not contribute directly to answering the query.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Construct a logical path from the filtered entities to the final answer by identifying chronological or categorical dependencies.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Validate the constructed path by cross-referencing with the original context to ensure no critical detail is missed.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Refine the answer by ensuring it is concise, accurate, and directly derived from the validated path.</instruction>
  </operator>
  <operator id="6" type="agent">
    <instruction>Check for consistency across all operators' outputs to ensure coherence and correctness of the final solution.</instruction>
  </operator>
  <operator id="7" type="agent">
    <instruction>Finalize the output by integrating the validated answer into the required format, ensuring clarity and precision.</instruction>
  </operator>