# Workflow ID: hotpotqa_81_0
# Benchmark: hotpotqa
# Data Indices: [951, 2303, 2302, 1992, 2438]

<agent id="1" type="reasoning">
        <instruction>Step 1: Identify the key subject and context of the question. Determine what unit is being asked about in relation to the admiral targeted by Operation Vengeance.</instruction>
    </agent>
    <agent id="2" type="search">
        <instruction>Step 2: Search for historical records or documents that detail the military structure of Japan during World War II, focusing on the admiral targeted by Operation Vengeance—Isoroku Yamamoto.</instruction>
    </agent>
    <agent id="3" type="analyze">
        <instruction>Step 3: Analyze the information retrieved to determine which Japanese naval unit was commanded by Isoroku Yamamoto at the time of Operation Vengeance.</instruction>
    </agent>
    <agent id="4" type="verify">
        <instruction>Step 4: Cross-check with reliable sources (e.g., official military histories, academic publications) to confirm the correct unit under Yamamoto's command during the operation.</instruction>
    </agent>
    <agent id="5" type="conclude">
        <instruction>Step 5: Based on verified data, conclude the name of the Japanese unit commanded by Admiral Isoroku Yamamoto during Operation Vengeance.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>