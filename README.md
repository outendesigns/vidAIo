# vidAIo
Simple server-side AI video clip analysis using Python and Claude AI

Outputs a simple JSON response as outlined in the Prompt.
### Prompt
"""You are a Security and Risk Analyst reviewing security footage. 

Analyze the provided frames and respond ONLY with valid JSON. Do not include any preamble, explanation, or markdown formatting - just the raw JSON object.

Use this exact structure:
{
  "vehicle_detected": boolean,
  "person_detected": boolean,
  "license_plates": [array of strings, empty if none visible],
  "possible_vehicle_accident": boolean,
  "smoke_detected": boolean,
  "fire_detected": boolean,
  "firearm_detected": boolean,
  "threat_level": integer 0-10,
  "summary": "string"
}

Threat level guidelines:
0-2: Normal activity, no concerns
3-4: Minor irregularities (loitering, unusual behavior)
5-6: Moderate concern (aggressive behavior, unsafe driving)
7-8: High concern (weapons visible, active conflict, fire/smoke)
9-10: Critical emergency (active shooter, major accident, widespread danger)"""
### Test Case One - Precision 15
BourbonStreet20251203at22.09.30_480p.mov

Output:
{
  "vehicle_detected": false,
  "person_detected": true,
  "license_plates": [],
  "possible_vehicle_accident": false,
  "smoke_detected": false,
  "fire_detected": false,
  "firearm_detected": false,
  "threat_level": 3,
  "summary": "Nighttime urban scene showing a wet street corner with multiple people gathered on sidewalks near commercial buildings. Large crowd congregated on corner storefront area, with additional pedestrians crossing the wet street throughout the sequence. Appears to be a social gathering or nightlife activity in an entertainment district. No vehicles, weapons, fire, or smoke detected. Minor concern due to crowd size and late-night activity which could indicate loitering or potential for disturbances, but no immediate threatening behavior observed. Situation warrants monitoring but does not appear to be an emergency."
}

### Test Case Two - Precision 20
AbbeyRoad20251202at06.03.31_480p.mov

Output:
{
  "vehicle_detected": true,
  "person_detected": false,
  "license_plates": [],
  "possible_vehicle_accident": false,
  "smoke_detected": false,
  "fire_detected": false,
  "firearm_detected": false,
  "threat_level": 1,
  "summary": "Normal nighttime traffic activity on wet road surface. Multiple vehicles observed traveling through intersection with traffic signals operational. Road appears wet, likely from recent rain. Vehicles maintaining normal speed and lane discipline. No pedestrians visible. No safety concerns detected. Standard urban traffic flow during evening/night hours."
}
