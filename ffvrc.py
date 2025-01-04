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
            style([BLUE, BOLD], self.language),
            style(ORANGE, self.codec, width=30),
            style(VIOLET, f'{self.sample_rate} Hz'),
            style(BLUE, f'{self.bit_rate} kbps'),
            style(GREEN, self.channel_layout),
        ])

@dataclasses.dataclass
class SubtitleStream:
    codec: str
    image: bool
    language: str
    title: str
    
    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            codec    = d.get('codec_long_name', '???'),
            image    = d.get('codec_name') in SubtitleStream.IMAGE_BASED_SUBS,
            language = d.get('tags', {}).get('language', '???'),
            title    = d.get('tags', {}).get('title'   , '???'),
        )
    
    def style(self) -> str:
        return ' '.join([
            style([BLUE, BOLD], self.language),
            style(AQUA, self.title, width=30),
            style(ORANGE, self.codec, width=30),
        ])

SubtitleStream.IMAGE_BASED_SUBS = ['dvb_subtitle', 'dvd_subtitle',
    'hdmv_pgs_subtitle', 'xubs']

########################
# CLI Argument Parsing #
########################

parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path,
    help='Input file to convert with ffmpeg.')
parser.add_argument('-o', '--output', type=Path,
    help='Output file [defaults to input filename with .vrc.mp4 extension]')
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
parser.add_argument('-sf', '--subtitle-file', type=Path,
    help='Select subtitle file')
parser.add_argument('--inspect', action='store_true', default=False,
    help='Inspect video file without converting [default false]')

args = parser.parse_args()
if args.inspect:
    for argument, value in vars(args).items():
        # These are the only two arguments allowed with --inpsect
        if argument in ['inspect', 'input', 'subtitle_file']:
            continue
        
        if value is not None:
            fail(f'Cannot use argument '
                f'{style([BOLD, MAGENTA], argument)} with '
                f'{style([BOLD, ORANGE], "--inspect")}')
if not args.input.exists():
    fail(f'Input file {style([BOLD, MAGENTA], args.input)} not found')
if args.subtitle_file:
    if not args.subtitle_file.exists():
        fail(f'Subtitle file {style([BOLD, MAGENTA], args.subtitle_file)} not '
            'found')
    if args.subtitle_file.suffix not in ['.srt', '.ass']:
        print(f'{style([BOLD, MAGENTA], "Warning:")} Subtitle files other than '
            '.srt and .ass may not be handled correctly\n')
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

def ffprobe(path: Path):
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            path,
        ], capture_output=True, text=True)
    except FileNotFoundError:
        fail(f'{style([BOLD, ORANGE], "ffprobe")} not found\n'
            f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed '
            f'correctly')
    if result.returncode:
        fail(f'{style([BOLD, ORANGE], "ffprobe")} returned code '
            f'{result.returncode}\n'
            f'  Check if input file {style([BOLD, MAGENTA], path)} is '
            f'malformed')
    try:
        return json.loads(result.stdout)['streams']
    except Exception as e:
        fail(f'Unable to parse JSON from {style([BOLD, ORANGE], "ffprobe")}\n'
            f'  {e.__repr__()}\n'
            f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed '
            f'correctly')

streams = {
    'video': [],
    'audio': [],
    'subtitle': [],
}

for s in ffprobe(args.input):
    # 10-bit H.264 videos have caused me compatibility headaches, especially
    # with Fedora's crippled version of ffmpeg. If an H.264 video appears to be
    # 10-bit, check if a proper H.264 codec is available and not just
    # libopenh264
    if s['codec_type'] == 'video' and s['codec_name'] == 'h264':
        # Yes ffmpeg reports bits_per_raw_sample as a string. Idk why. Also it
        # seem to be present only rarely
        if '10' in s.get('codec_long_name', '') \
        or s.get('bits_per_raw_sample') == '10':
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-decoders',
            ], capture_output=True, text=True)
            
            if result.returncode:
                fail(f'{style([BOLD, ORANGE], "ffprobe")} returned code '
                    f'{result.returncode} while checking H.264 support\n'
                    f'  Something is very wrong!')
            
            h264_decoders = re.findall(
                'V[A-Z.]{4}D ([a-zA-Z0-9_]*h264[a-zA-Z0-9_]*)', result.stdout)
            
            if 'h264' not in h264_decoders:
                print(f'{style([BOLD, MAGENTA], "Warning:")} This appears to '
                    f'be a 10-bit H.264 video, and the standard H.264 '
                    f'decoder does not appear to be present. Other H.264 '
                    f'decoders frequently crash on 10-bit video. If this is a '
                    f'FOSS-only build of ffmpeg, consider getting a full '
                    f'build.\n'
                    f'  {style([BOLD, ORANGE], "ffmpeg")} found decoders: '
                    f'{style([BOLD, ORANGE], ', '.join(h264_decoders))}\n'
                    f'  Attempting to convert the video anyway...\n')
    
    match s['codec_type']:
        case 'video'   : streams['video'   ].append(VideoStream   .from_dict(s))
        case 'audio'   : streams['audio'   ].append(AudioStream   .from_dict(s))
        case 'subtitle': streams['subtitle'].append(SubtitleStream.from_dict(s))

# If a subtitle file is supplied, ignore any subtitle streams in the video file
if args.subtitle_file:
    streams['subtitle'] = [SubtitleStream.from_dict(s)
        for s in ffprobe(args.subtitle_file) if s['codec_type'] == 'subtitle']

selections = {
    'video': None,
    'audio': None,
    'subtitle': None,
    'image_subtitles': False,
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
    if codec_type == 'subtitle' and selection \
    and streams['subtitle'][selection - 1].image:
        selections['image_subtitles'] = True
    
    # When no video stream is selected, several CLI options are prohibited
    if codec_type == 'video' and selection == 0:
        for argument in [
            'resolution', 'framerate', 'subtitle_stream', 'subtitle_file',
        ]:
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

# Video filters will be empty if -vn is set. This is enforced earlier when
# CLI arguments are checked
video_filters = []

# Since video formats are the most cursed formats, subtitle streams aren't
# always text: Sometimes they're images! ffmpeg can handle that, but regular
# video filters won't do - it needs -filter_complex, which is just as
# complicated to figure out as the name suggests. It must be applied before
# mapping the video stream, and the -map argument must use -filter_complex's
# output, else the subtitles won't be baked into the final video
#
# Note: If subtitles are used they must be the first filter, otherwise they will
# end up in the wrong spot on the video
#
# Note: Subtitle files with multiple subtitle streams aren't handled, because I
# haven't seen any in the wild and don't know if they exist
#
# Note: Subtitle files that use images aren't handled either, because I haven't
# seen any in the wild and don't know if they exist
if selections['subtitle']:
    if selections['image_subtitles']:
        video_filters += ['overlay']
    elif args.subtitle_file:
        filter_type = 'ass' if args.subtitle_file.suffix == '.ass' \
            else 'subtitles'
        
        # Subtitle must be quoted with single quotes for ffmpeg
        video_filters += [f'{filter_type}=\'{args.subtitle_file}\'']
    else:
        # Subtitle must be quoted with single quotes for ffmpeg
        video_filters += [f'subtitles=\'{args.input}\':'
            f'si={selections["subtitle"] - 1}']

# These filters can be applied using -vf, but -vf and -filter_complex do not
# work together so everything has to use -filter_complex
if args.resolution: video_filters += [f'scale={args.resolution}']
if args.framerate : video_filters += [f'fps={  args.framerate }']

if len(video_filters):
    video_source = f'[0:v:{selections["video"] - 1}]'
    if selections['image_subtitles']:
        video_source += f'[0:s:{selections["subtitle"] - 1}]'
    
    ffmpeg_command += ['-filter_complex',
         video_source + ','.join(video_filters) + '[vout]']

ffmpeg_command += ['-vn'] if selections['video'] == 0 else [
    '-map', '[vout]' if video_filters else f'0:v:{selections["video"] - 1}',
    '-c:v', 'h264',
    '-preset', 'veryslow',
    '-movflags', '+faststart',
]

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
    # Double-quote fields with paths so printed command works in most shells.
    # The value passed to -filter_complex always ends in "[vout]". -map may also
    # have a value of "[vout]", in which case it should probably be quoted too
    f'"{token}"' if isinstance(token, Path) or token[-6:] == '[vout]' else token
for token in ffmpeg_command)))

try:
    ffmpeg_result = subprocess.run(ffmpeg_command)
except FileNotFoundError:
    fail(f'{style([BOLD, ORANGE], "ffmpeg")} not found\n'
        f'  Check if {style([BOLD, ORANGE], "ffmpeg")} is installed correctly')
except KeyboardInterrupt:
    print() # ffmpeg may leave the cursor in the middle of a line
    fail('Canceled by user')
if ffmpeg_result.returncode:
    fail(f'{style([BOLD, ORANGE], "ffmpeg")} returned code '
        f'{ffmpeg_result.returncode}\n'
        f'  Check if input file {style([BOLD, MAGENTA], args.input)} is '
        f'malformed')
