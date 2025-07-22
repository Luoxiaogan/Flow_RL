# Workflow ID: drop_752_0
# Benchmark: drop
# Data Indices: [2563, 1080, 936, 1988, 3005]

<start>
        <task>Extract relevant information from input</task>
        <next>analyze_question</next>
    </start>

    <node id="analyze_question">
        <task>Understand the question structure and identify required data points</task>
        <next>locate_data</next>
    </node>

    <node id="locate_data">
        <task>Search passage for values or facts directly answering the question</task>
        <next>validate_and_process</next>
    </node>

    <node id="validate_and_process">
        <task>Verify that extracted data is accurate and compute required result</task>
        <next>check_complexity</next>
    </node>

    <node id="check_complexity">
        <task>Determine if solution requires multiple steps or reasoning</task>
        <conditional>
            <if condition="complex">
                <next>multi_step_reasoning</next>
            </if>
            <else>
                <next>generate_answer</next>
            </else>
        </conditional>
    </node>

    <node id="multi_step_reasoning">
        <task>Apply step-by-step logical processing to derive answer</task>
        <next>generate_answer</next>
    </node>

    <node id="generate_answer">
        <task>Produce final numerical or textual response based on processed data</task>
        <next>end</next>
    </node>

    <end>
        <output>Final answer</output>
    </end>