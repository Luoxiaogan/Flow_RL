# Workflow ID: hotpotqa_210_0
# Benchmark: hotpotqa
# Data Indices: [3726, 2099, 2911, 3597, 26]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on the main subject, its attributes, and any associated locations or contexts.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    
    <operator id="1">
        <instruction>Extract the specific question being asked. Determine what information is required to answer it directly from the context provided.</instruction>
        <input>entity_analysis</input>
        <output>question_identification</output>
    </operator>
    
    <operator id="2">
        <instruction>Locate all relevant contextual sentences that contain direct or indirect answers to the question. Prioritize those with explicit mentions of the subject, action, or location.</instruction>
        <input>question_identification</input>
        <output>context_extraction</output>
    </operator>
    
    <operator id="3">
        <instruction>Filter and refine the extracted context to remove irrelevant details. Keep only the data that directly supports answering the question.</instruction>
        <input>context_extraction</input>
        <output>filtered_context</output>
    </operator>
    
    <operator id="4">
        <instruction>Map the filtered context to the exact answer by identifying the correct entity or value that satisfies the question's requirements.</instruction>
        <input>filtered_context</input>
        <output>answer_mapping</output>
    </operator>
    
    <operator id="5">
        <instruction>Verify the correctness of the mapped answer against the original question and context. Ensure no ambiguity remains and the answer is fully supported.</instruction>
        <input>answer_mapping</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="6">
        <instruction>Format the final answer in a clear and concise manner, ensuring it matches the expected output type (e.g., name, number, location).</instruction>
        <input>final_answer</input>
        <output>formatted_output</output>
    </operator>