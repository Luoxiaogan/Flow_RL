# Workflow ID: hotpotqa_217_0
# Benchmark: hotpotqa
# Data Indices: [3731, 3028, 33, 3536]

<operator id="0" type="extract">
    <prompt>Extract the key entities and relationships from the input context relevant to the question.</prompt>
  </operator>
  <operator id="1" type="reason">
    <prompt>Reason step-by-step about how the extracted entities relate to the question. Focus on identifying direct matches or logical inferences.</prompt>
  </operator>
  <operator id="2" type="validate">
    <prompt>Validate if the reasoning leads to a single, unambiguous answer. If not, identify the missing link or ambiguity.</prompt>
  </operator>
  <operator id="3" type="resolve">
    <prompt>If validation fails, resolve ambiguity by cross-referencing with other parts of the context or applying domain knowledge.</prompt>
  </operator>
  <operator id="4" type="synthesize">
    <prompt>Synthesize the validated information into a clear, concise final answer.</prompt>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>