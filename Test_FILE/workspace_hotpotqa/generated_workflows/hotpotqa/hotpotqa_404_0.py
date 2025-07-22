# Workflow ID: hotpotqa_404_0
# Benchmark: hotpotqa
# Data Indices: [2982, 2913, 477, 1076]

<node id="start" type="input">
        <task>Receive problem input</task>
    </node>
    
    <node id="analyze_question" type="agent">
        <task>Parse and understand the core question</task>
        <depends_on>start</depends_on>
    </node>
    
    <node id="extract_context" type="agent">
        <task>Identify relevant context from provided text</task>
        <depends_on>analyze_question</tasks>
    </node>
    
    <node id="match_info" type="agent">
        <task>Map contextual clues to answer candidates</task>
        <depends_on>extract_context</depends_on>
    </node>
    
    <node id="validate_candidates" type="agent">
        <task>Check consistency of matches against all evidence</task>
        <depends_on>match_info</depends_on>
    </node>
    
    <node id="generate_answer" type="agent">
        <task>Construct final answer based on validated info</task>
        <depends_on>validate_candidates</depends_on>
    </node>
    
    <node id="output" type="output">
        <task>Return the answer</task>
        <depends_on>generate_answer</depends_on>
    </node>
    
    <edge from="start" to="analyze_question"/>
    <edge from="analyze_question" to="extract_context"/>
    <edge from="extract_context" to="match_info"/>
    <edge from="match_info" to="validate_candidates"/>
    <edge from="validate_candidates" to="generate_answer"/>
    <edge from="generate_answer" to="output"/>