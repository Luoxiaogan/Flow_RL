# Workflow ID: drop_709_0
# Benchmark: drop
# Data Indices: [2712, 3589, 2113, 12, 190]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant data from the passage that answers the question. Focus on identifying all instances of the required events (e.g., touchdowns, field goals, distances, percentages).</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Process the extracted data to compute the required metric (e.g., difference between touchdowns and field goals, percentage of non-English residents, etc.). Apply mathematical operations carefully.</instruction>
        <input>2</input>
        <output>computed_result</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify the computed result by cross-checking with original passage details. Ensure no misinterpretation occurred during extraction or calculation.</instruction>
        <input>2,3</input>
        <output>verified_result</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Format the verified result into a clear, concise answer tailored to the specific question asked. Avoid ambiguity or extra information.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    
    <node id="6" type="output">
        <param name="answer" value="final_answer" />
    </node>