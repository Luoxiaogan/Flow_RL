# Workflow ID: hotpotqa_486_0
# Benchmark: hotpotqa
# Data Indices: [3723, 977, 101, 749, 1218]

<operator id="1" type="extract">
        <input>problem</input>
        <output>extracted_question, extracted_context</output>
        <instruction>Extract the main question and relevant context from the input problem.</instruction>
    </operator>
    
    <operator id="2" type="parse">
        <input>extracted_context</input>
        <output>parsed_entities</output>
        <instruction>Parse the context to identify key entities such as names, dates, organizations, and relationships.</instruction>
    </operator>
    
    <operator id="3" type="reason">
        <input>parsed_entities, extracted_question</input>
        <output>intermediate_solution</output>
        <instruction>Reason step-by-step: Identify which entity in the context directly answers the question. If multiple candidates exist, filter based on relevance to the question's focus (e.g., birth date, role, relationship).</instruction>
    </operator>
    
    <operator id="4" type="validate">
        <input>intermediate_solution</input>
        <output>final_answer</output>
        <instruction>Validate that the intermediate solution matches the question exactly — e.g., if the question asks for a birth date, ensure the answer is in YYYY-MM-DD format or equivalent. Reject any ambiguous or incomplete responses.</instruction>
    </operator>
    
    <operator id="5" type="assemble">
        <input>final_answer</input>
        <output>complete_output</output>
        <instruction>Format the final answer as a clean string with no extra text, just the answer itself.</instruction>
    </operator>