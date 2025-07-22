# Workflow ID: drop_849_0
# Benchmark: drop
# Data Indices: [688, 2318, 2964, 2069, 2844]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="process">
        <operation>extract_key_info</operation>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="process">
        <operation>analyze_context</operation>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="decision">
        <condition>is_numerical_question</condition>
        <depends_on>3</depends_on>
        <true>5</true>
        <false>6</false>
    </node>
    <node id="5" type="output">
        <operation>return_numeric_answer</operation>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <operation>return_categorical_answer</operation>
        <depends_on>4</depends_on>
    </node>