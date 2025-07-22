# Workflow ID: hotpotqa_191_0
# Benchmark: hotpotqa
# Data Indices: [814, 226, 1838, 2084]

<operator id="1" type="extract">
        <input>problem</input>
        <output>extracted_question, extracted_context</output>
        <instruction>Extract the main question and relevant context from the input problem.</instruction>
    </operator>

    <operator id="2" type="analyze">
        <input>extracted_question, extracted_context</input>
        <output>analysis_result</output>
        <instruction>Step-by-step analyze the question and context to identify key entities, relationships, and constraints. Focus on what needs to be determined and what information is available.</instruction>
    </operator>

    <operator id="3" type="reason">
        <input>analysis_result</input>
        <output>reasoning_steps</output>
        <instruction>Reason through the problem step by step using logical deduction. Identify how each piece of context supports or contradicts possible answers.</instruction>
    </operator>

    <operator id="4" type="validate">
        <input>reasoning_steps</input>
        <output>valid_solutions</output>
        <instruction>Validate each reasoning path against the context. Eliminate any options that contradict given facts or lack sufficient evidence.</instruction>
    </operator>

    <operator id="5" type="synthesize">
        <input>valid_solutions</input>
        <output>final_answer</output>
        <instruction>Combine validated solutions into a single coherent answer. Ensure it directly addresses the original question with clarity and precision.</instruction>
    </operator>

    <operator id="6" type="verify">
        <input>final_answer</input>
        <output>verification_result</output>
        <instruction>Double-check the final answer against all provided context to ensure accuracy and completeness. Confirm no critical details were missed.</instruction>
    </operator>

    <connection>
        <from>1</from>
        <to>2</to>
    </connection>
    <connection>
        <from>2</from>
        <to>3</to>
    </connection>
    <connection>
        <from>3</from>
        <to>4</to>
    </connection>
    <connection>
        <from>4</from>
        <to>5</to>
    </connection>
    <connection>
        <from>5</from>
        <to>6</to>
    </connection>