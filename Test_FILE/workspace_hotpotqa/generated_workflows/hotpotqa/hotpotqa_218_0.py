# Workflow ID: hotpotqa_218_0
# Benchmark: hotpotqa
# Data Indices: [1420, 318, 3840, 3009]

<operator id="1" type="agent">
    <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components and determine what information is needed to solve it.</instruction>
    <output>Extracted entities and required information</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Search for relevant context that directly addresses the question. Focus on specific details that match the entities or concepts mentioned in the problem.</instruction>
    <output>Relevant context snippets identified</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Validate the relevance of each context snippet. Filter out any information that does not contribute to answering the question.</instruction>
    <output>Filtered and validated context</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Combine the validated context to form a coherent answer. Ensure logical consistency and completeness based on the filtered information.</instruction>
    <output>Final answer derived from combined context</output>
  </operator>
  <operator id="5" type="agent">
    <instruction>Review the final answer for accuracy, clarity, and alignment with the question. Make sure no critical detail is missing or misrepresented.</instruction>
    <output>Verified and refined final answer</output>
  </operator>
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />