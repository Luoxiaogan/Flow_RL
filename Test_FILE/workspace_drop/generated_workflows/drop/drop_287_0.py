# Workflow ID: drop_287_0
# Benchmark: drop
# Data Indices: [1369, 2570, 3189, 1060]

<node id="1">
        <input>problem</input>
        <output>extract_question</output>
        <operator>extract_question</operator>
    </node>
    <node id="2">
        <input>problem</input>
        <output>extract_passage</output>
        <operator>extract_passage</operator>
    </node>
    <node id="3">
        <input>extract_question</input>
        <output>identify_key_terms</output>
        <operator>identify_key_terms</operator>
    </node>
    <node id="4">
        <input>extract_passage</input>
        <output>parse_context</output>
        <operator>parse_context</operator>
    </node>
    <node id="5">
        <input>identify_key_terms</input>
        <input>parse_context</output>
        <output>match_evidence</output>
        <operator>match_evidence</operator>
    </node>
    <node id="6">
        <input>match_evidence</input>
        <output>validate_answer</output>
        <operator>validate_answer</operator>
    </node>
    <node id="7">
        <input>validate_answer</input>
        <output>final_answer</output>
        <operator>format_answer</operator>
    </node>