# Workflow ID: drop_455_0
# Benchmark: drop
# Data Indices: [715, 3390, 3645, 1325, 683]

<node id="1">
        <input>problem</input>
        <output>extract_question</output>
        <agent>ExtractQuestionAgent</agent>
    </node>
    <node id="2">
        <input>problem</input>
        <output>extract_passage</output>
        <agent>ExtractPassageAgent</agent>
    </node>
    <node id="3">
        <input>extract_question, extract_passage</input>
        <output>identify_key_info</output>
        <agent>IdentifyKeyInfoAgent</agent>
    </node>
    <node id="4">
        <input>identify_key_info</input>
        <output>generate_answer</output>
        <agent>GenerateAnswerAgent</agent>
    </node>
    <node id="5">
        <input>generate_answer</input>
        <output>validate_answer</output>
        <agent>ValidateAnswerAgent</agent>
    </node>
    <node id="6">
        <input>validate_answer</input>
        <output>final_answer</output>
        <agent>FinalAnswerAgent</agent>
    </node>
    <edge from="1" to="3"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>