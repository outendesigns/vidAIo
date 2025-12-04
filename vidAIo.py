import argparse
import os
import subprocess
import anthropic
import base64
import json
import shutil

def get_video_duration(filepath):
  command = [
    "ffprobe",
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    filepath
  ]  
  try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    duration_str = result.stdout.strip()
    if duration_str:
      return float(duration_str)
    else:
      return None
  except subprocess.CalledProcessError as e:
    print(f"Error running ffprobe: {e.stderr}")
    return None
  except ValueError:
    print(f"Could not parse duration from ffprobe output: {duration_str}")
    return None

def extract_frames(video_path, interval_seconds, output_dir='frames', verbose=False):
  os.makedirs(output_dir, exist_ok=True)
  output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
  command = [
    'ffmpeg',
    '-i', video_path,
    '-vf', f'fps=1/{interval_seconds}',
    '-q:v', '2',
    output_pattern
  ]
  try:
    if verbose:
      print(f"Extracting frames every {interval_seconds} seconds...")
    result = subprocess.run(
      command,
      capture_output=True,
      text=True,
      check=True
    )
    if verbose:
      print(f"Frames saved to {output_dir}/")
        
    # Count extracted frames
    frame_count = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
    if verbose:
      print(f"Total frames extracted: {frame_count}")
        
  except subprocess.CalledProcessError as e:
    print(f"Error running ffmpeg: {e}")
    print(f"stderr: {e.stderr}")

def encode_image_b64(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode("utf-8")

def main():
  parser = argparse.ArgumentParser(description="")

  parser.add_argument(
    'filepath',
    type=str,
    help='Path to the input file'
  )

  parser.add_argument(
    '-p', '--precision',
    type=int,
    default=5,
    help='How many frames within the total video should be processed.'
  )

  parser.add_argument(
    '-o', '--output',
    default='frames',
    help='Output directory for frames (default: frames)'
  )

  parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Enable print verbosity for debugging'
  )

  args = parser.parse_args()

  # Confirm the file exists
  if not os.path.isfile(args.filepath):
    parser.error(f"File does not exist: {args.filepath}")

  videoDuration = get_video_duration(args.filepath)
  precisionGap = int(round(videoDuration)/args.precision)

  if args.verbose:
    print(f"Processing file: {args.filepath}")
    print(f"Processing with precision level: {args.precision}")
    print(f"Length of the video is: {videoDuration} seconds")
    print(f"precisionGap is: {precisionGap} seconds.")

  extract_frames(args.filepath, precisionGap, args.output, args.verbose)

  client = anthropic.Anthropic()

  content = []

  for filename in sorted(os.listdir(args.output)):
    if filename.endswith(".jpg"):
      image_path = os.path.join(args.output, filename)
      content.append({
        "type": "image",
        "source": {
          "type": "base64",
          "media_type": "image/jpeg",
          "data": encode_image_b64(image_path)
        }
      })

  content.append({
    "type": "text",
    "text": """You are a Security and Risk Analyst reviewing security footage. 

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
  })

  message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    temperature=0.3,
    system="""You are a Security and Risk Analyst reviewing security footage. 

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
9-10: Critical emergency (active shooter, major accident, widespread danger)""",
    messages=[
      {
        "role": "user",
        "content": content
      }
    ]
  )

  # Clean Up Claudes Response and Format as JSON properly
  response_text = message.content[0].text.strip()
  if response_text.startswith("```json"):
    response_text = response_text.split("```json")[1].split("```")[0].strip()
  elif response_text.startswith("```"):
    response_text = response_text.split("```")[1].split("```")[0].strip()
  analysis = json.loads(response_text)
  print(json.dumps(analysis, indent=2))

  if os.path.exists(args.output):
    try:
      shutil.rmtree(args.output)
      if args.verbose:
        print(f"Deleted the {args.output} directory and extracted frames.")
    except OSError as e:
      if args.verbose:
        print(f"Error: {args.output} : {e.strerror}")
  else:
    if args.verbose:
      print(f"Folder {args.output} does not exist.")

  print("Completed")

if __name__ == '__main__':
  main()
