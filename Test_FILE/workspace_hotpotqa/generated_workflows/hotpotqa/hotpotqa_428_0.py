# Workflow ID: hotpotqa_428_0
# Benchmark: hotpotqa
# Data Indices: [2406, 3330, 1146, 2978]

<agent id="1">
        <instruction>Identify the key entity in the question and locate its associated details in the context.</instruction>
        <input>problem</input>
        <output>entity_details</output>
    </agent>
    <agent id="2">
        <instruction>Extract numerical values related to the entity, focusing on capacity or seating numbers if applicable.</instruction>
        <input>entity_details</input>
        <output>seating_capacity</output>
    </agent>
    <agent id="3">
        <instruction>Verify that the extracted number corresponds to the correct venue and matches the description (e.g., arched-roof building).</instruction>
        <input>seating_capacity</input>
        <output>verified_number</output>
    </agent>
    <agent id="4">
        <instruction>Ensure the answer is formatted as a single integer with no additional text or units.</instruction>
        <input>verified_number</input>
        <output>final_answer</output>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>