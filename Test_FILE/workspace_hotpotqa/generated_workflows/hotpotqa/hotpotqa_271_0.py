# Workflow ID: hotpotqa_271_0
# Benchmark: hotpotqa
# Data Indices: [3770, 3138, 354, 1841, 2483]

<agent id="1" type="reasoning">
    <instruction>Think step by step to identify the correct answer based on the context provided.</instruction>
    <input>problem</input>
    <output>step_by_step_analysis</output>
  </agent>
  
  <agent id="2" type="extraction">
    <instruction>Extract key entities and relationships from the context that are relevant to the question.</instruction>
    <input>problem</input>
    <output>key_entities</output>
  </agent>
  
  <agent id="3" type="verification">
    <instruction>Verify if the extracted entities match the question's requirements. If not, refine the extraction.</instruction>
    <input>key_entities</input>
    <output>verified_entities</output>
  </agent>
  
  <agent id="4" type="synthesis">
    <instruction>Combine the verified entities with the step-by-step reasoning to derive a final answer.</instruction>
    <input>verified_entities, step_by_step_analysis</input>
    <output>final_answer</output>
  </agent>
  
  <agent id="5" type="validation">
    <instruction>Validate the final answer against all provided context to ensure correctness and completeness.</instruction>
    <input>final_answer, problem</input>
    <output>validated_answer</output>
  </agent>
  
  <edge from="1" to="4"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>