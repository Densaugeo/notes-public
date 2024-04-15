#!/bin/python
import argparse, subprocess, json, dataclasses, re, sys
from pathlib import Path
from typing import List

####################
# Helper Functions #
####################

def style(styles: List[str | int], string: object = '',
width: int | None = None) -> str:
    string = str(string)
    
    if width is not None:
        assert width > 0
        
        if len(string) <= width: string = f'{string:{width}}'
        else: string = string[:max(width - 3, 0)] + min(width, 3)*'.'
    
    ansi_codes = ''
    
    if not isinstance(styles, list):
        styles = [styles]
    
    for style in styles:
        match style:
            case int():
                ansi_codes += f'\033[{style}m'
            case str() if re.fullmatch('#[0-9a-fA-F]{3}', style):
                r, g, b = (int(style[i], 16)*0xff//0xf for i in [1, 2, 3])
                ansi_codes += f'\033[38;2;{r};{g};{b}m'
            case str() if re.fullmatch('#[0-9a-fA-F]{6}', style):
                r, g, b = (int(style[i:i+2], 16) for i in [1, 3, 5])
                ansi_codes += f'\033[38;2;{r};{g};{b}m'
            case _:
                raise ValueError(f'Unknown style: {style}')
    
    reset = '\033[0m' if styles and string else ''
    
    return ansi_codes + string + reset

RESET = 0
BOLD = 1
GRAY = '#ccc'
MAGENTA = '#f0f'
VIOLET = '#c6f'
BLUE = '#4ad'
AQUA = '#1aba97'
GREEN = '#4d4'
ORANGE = '#ecb64a'
RED = '#f00'

def fail(message: str):
    print(f'{style([BOLD, RED], "Error:")} {message}')
    sys.exit(1)

###############
# Dataclasses #
###############

@dataclasses.dataclass
class VideoStream:
    codec: str
    language: str
    resolution: str
    frame_rate: str
    
    @classmethod
    def from_dict(cls, d: dict):
        try:
            resolution = f'{d["width"]}:{d["height"]}'
        except:
            resolution = '???'
        
        try:
            numerator, denominator = d.get('r_frame_rate').split('/')
            frame_rate = f'{int(numerator)/int(denominator):.3f}'
        except:
            frame_rate = '???'
        
        return cls(
            codec      = d.get('codec_long_name', '???'),
            language   = d.get('tags', {}).get('language', '???'),
            resolution = resolution,
            frame_rate = frame_rate,
        )
    
    def style(self) -> str:
        return ' '.join([
            style([BLUE, BOLD], self.language),
            style(ORANGE, self.codec, width=50),
            style(GREEN, self.resolution),
            style(GRAY, '@'),
            style(VIOLET, f'{self.frame_rate} fps'),
        ])

@dataclasses.dataclass
class AudioStream:
    codec: str
    language: str
    channel_layout: str
    sample_rate: str
    bit_rate: str
    
    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            codec          = d.get('codec_long_name', '???'),
            language       = d.get('tags', {}).get('language', '???'),
            channel_layout = d.get('channel_layout' , '???'),
            sample_rate    = d.get('sample_rate'    , '???'),
            bit_rate       = d.get('bit_rate'       , '???'),
        )
    
    def style(self) -> str:
        return ' '.join([
            style([BLUE, BOLD], stream.language),
            style(ORANGE, stream.codec, width=30),
            style(VIOLET, f'{stream.sample_rate} Hz'),
            style(BLUE, f'{stream.bit_rate} kbps'),
            style(GREEN, stream.channel_layout),
        ])

@dataclasses.dataclass
class SubtitleStream:
    codec: str
    language: str
    title: str
    
    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            codec    = d.get('codec_long_name', '???'),
            language = d.get('tags', {}).get('language', '???'),
            title    = d.get('tags', {}).get('title   ', '???'),
        )
    
    def style(self) -> str:
        return ' '.join([
            style([BLUE, BOLD], stream.language),
            style(AQUA, stream.title, width=30),
            style(ORANGE, stream.codec, width=30),
        ])

########################
# CLI Argument Parsing #
########################

parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path,
    help='Input file to convert with ffmpeg.')
parser.add_argument('-o', '--output', type=Path,
    help='Output file [defaults to input filename with .mp4 extension]')
parser.add_argument('-r', '--resolution', type=str,
    help='Output video resolution [defaults to input video resolution]')
parser.add_argument('-f', '--framerate', type=float,
    help='Output video framerate [defaults to input video framerate]')
parser.add_argument('-vs', '--video-stream', type=int,
    help='Select video stream (0 to skip video)')
parser.add_argument('-as', '--audio-stream', type=int,
    help='Select audio stream (0 to skip audio)')
parser.add_argument('-ss', '--subtitle-stream', type=int,
    help='Select subtitle stream (0 to skip subtitles)')
parser.add_argument('--inspect', action='store_true', default=False,
    help='Inspect video file without converting [default false]')

args = parser.parse_args()
if args.inspect:
    for argument, value in vars(args).items():
        # These are the only two arguments allowed with --inpsect
        if argument in ['inspect', 'input']:
            continue
        
        if value is not None:
            fail(f'Cannot use argument '
                f'{style([BOLD, MAGENTA], argument)} with '
                f'{style([BOLD, ORANGE], "--inspect")}')
if not args.input.exists():
    fail(f'Input file {style([BOLD, MAGENTA], args.input)} not found')
if args.output is None:
    args.output = args.input.with_suffix('.vrc.mp4')
elif args.output.suffix != '.mp4':
    fail(f'Output file {style([BOLD, MAGENTA], args.output)} does not end in '
        f'{style([BOLD, ORANGE], ".mp4")}\n'
        f'  VRChat videos should use the {style([BOLD, ORANGE], ".mp4")} '
        f'extension for best compatibility with Unity\n'
        f'  video players')

###########
# ffprobe #
###########

try:
    ffprobe_result = subprocess.run([
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        args.input,
    ], capture_output=True, text=True)
except FileNotFoundError:
    fail(f'{style([BOLD, ORANGE], "ffprobe")} not found\n'
        f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed correctly')
if ffprobe_result.returncode:
    fail(f'{style([BOLD, ORANGE], "ffprobe")} returned code '
        f'{ffprobe_result.returncode}\n'
        f'  Check if input file {style([BOLD, MAGENTA], args.input)} is '
        f'malformed')
try:
    streams_json = json.loads(ffprobe_result.stdout)['streams']
except Exception as e:
    fail(f'Unable to parse JSON from {style([BOLD, ORANGE], "ffprobe")}\n'
        f'  {e.__repr__()}\n'
        f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed correctly')

streams = {
    'video': [],
    'audio': [],
    'subtitle': [],
}

for s in streams_json:
    match s['codec_type']:
        case 'video'   : streams['video'   ].append(VideoStream   .from_dict(s))
        case 'audio'   : streams['audio'   ].append(AudioStream   .from_dict(s))
        case 'subtitle': streams['subtitle'].append(SubtitleStream.from_dict(s))

selections = {
    'video': [],
    'audio': [],
    'subtitle': [],
}

for codec_type in streams:
    stream_count = len(streams[codec_type])
    
    print(f'Found {stream_count} {style([BOLD, AQUA], codec_type)} stream(s)')
    for i, stream in enumerate(streams[codec_type]):
        print(f'{style(BOLD)}[{i + 1:2}]{style(RESET)} - {stream.style()}')
    
    if args.inspect:
        print()
        continue
    
    selection = getattr(args, codec_type + '_stream')
    
    # If there's no video stream, subtitles can't be baked in
    if codec_type == 'subtitle' and selections['video'] == 0:
        selection = 0
    
    # Apply general defaults for 0 or 1 streams
    if selection is None:
        if 0 <= stream_count <= 1:
            selection = stream_count
    
    if selection is not None:
        print(' '.join([
            style(GRAY, 'Automatically selected stream:'),
            style([BOLD, MAGENTA], selection or 'none'),
        ]))
    
    # Seek user input if no stream was selected automatically
    if selection is None:
        selection = input('Select stream (0 for none): ' +
            style([BOLD, MAGENTA]))
        print(style(RESET), end='')
        
        if selection == '':
            fail('No value entered')
        
        try:
            selection = int(selection)
        except ValueError:
            fail(f'{style([BOLD, MAGENTA], selection)} is not a valid integer')
    
    if not 0 <= selection <= len(streams[codec_type]):
        fail('Cannot find requested stream '
            f'{style([BOLD, MAGENTA], selection)}')
    
    selections[codec_type] = selection
    
    # When no video stream is selected, several CLI options are prohibited
    if codec_type == 'video' and selection == 0:
        for argument in ['resolution', 'framerate', 'subtitle_stream']:
            if getattr(args, argument):
                fail(f'Cannot use argument '
                    f'{style([BOLD, MAGENTA], argument)} because no video '
                    f'stream is selected')
    
    print()

if args.inspect:
    sys.exit(0)

##########
# ffmpeg #
##########

ffmpeg_command = [
    'ffmpeg',
    '-hide_banner',
    '-v', 'quiet',
    '-stats',
    '-stats_period', '60',
    '-strict', '2',
    '-i', args.input,
]

ffmpeg_command += ['-vn'] if selections['video'] == 0 else [
    '-map', f'0:v:{selections["video"] - 1}',
    '-c:v', 'h264',
    '-preset', 'veryslow',
    '-movflags', '+faststart',
]

# Video filters will be empty if -vn is set. This is enforced earlier when
# CLI arguments are checked
video_filters = []
if args.resolution: video_filters += [f'scale={args.resolution}']
if args.framerate : video_filters += [f'fps={args.framerate   }']
if selections['subtitle']: video_filters += [
    # Subtitle must be quoted with single quotes for ffmpeg
    f'subtitles=\'{args.input}\':si={selections["subtitle"] - 1}'
]
if len(video_filters):
    ffmpeg_command += ['-vf', ','.join(video_filters)]

ffmpeg_command += ['-an'] if selections['audio'] == 0 else [
    '-map', f'0:a:{selections["audio"] - 1}',
    '-c:a', 'aac',
    '-ab', '320k',
]

# Must be at end, or some earlier arguments will be ignored
ffmpeg_command += [args.output]

print(f'Starting {style([BOLD, ORANGE], "ffmpeg")} (progress will update once '
    f'per minute)...')
print(style(ORANGE, ' '.join(
    # Double-quote fields with paths so printed command works in most shells
    f'"{token}"' if isinstance(token, Path) or 'subtitle' in token else token
for token in ffmpeg_command)))

try:
    ffmpeg_result = subprocess.run(ffmpeg_command)
except FileNotFoundError:
    fail(f'{style([BOLD, ORANGE], "ffmpeg")} not found\n'
        f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed correctly')
if ffmpeg_result.returncode:
    fail(f'{style([BOLD, ORANGE], "ffmpeg")} returned code '
        f'{ffmpeg_result.returncode}\n'
        f'  Check if input file {style([BOLD, MAGENTA], args.input)} is '
        f'malformed')
