# Workflow ID: hotpotqa_63_0
# Benchmark: hotpotqa
# Data Indices: [3937, 254, 1377, 2453, 3243]

<node id="1">
    <operator>QuestionAnalyzer</operator>
    <input>problem</input>
    <output>analyzed_question</output>
  </node>
  <node id="2">
    <operator>ContextExtractor</operator>
    <input>problem</input>
    <output>relevant_context</output>
  </node>
  <node id="3">
    <operator>EntityResolver</operator>
    <input>relevant_context</input>
    <output>key_entities</output>
  </node>
  <node id="4">
    <operator>RelationMapper</operator>
    <input>key_entities</input>
    <output>relationships</output>
  </node>
  <node id="5">
    <operator>LogicEngine</operator>
    <input>relationships</input>
    <output>reasoning_steps</output>
  </node>
  <node id="6">
    <operator>SolutionGenerator</operator>
    <input>reasoning_steps</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="4"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>