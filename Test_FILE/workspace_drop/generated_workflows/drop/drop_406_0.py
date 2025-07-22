# Workflow ID: drop_406_0
# Benchmark: drop
# Data Indices: [517, 1983, 1028, 3367, 554]

<node id="1">
        <input>problem</input>
        <output>extracted_question, extracted_passage</output>
        <agent>ExtractQuestionAndPassage</agent>
    </node>
    <node id="2">
        <input>extracted_question</input>
        <output>question_type</output>
        <agent>DetermineQuestionType</agent>
    </node>
    <node id="3">
        <input>extracted_passage</input>
        <output>parsed_events</output>
        <agent>ParsePassageIntoEvents</agent>
    </node>
    <node id="4">
        <input>parsed_events, extracted_question</input>
        <output>relevant_context</output>
        <agent>IdentifyRelevantContext</agent>
    </node>
    <node id="5">
        <input>relevant_context</input>
        <output>answer</output>
        <agent>GenerateAnswerFromContext</agent>
    </node>
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>