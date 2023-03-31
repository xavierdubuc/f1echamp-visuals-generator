from typing import List
from models import Pilot
from helpers.generator_config import GeneratorConfig
from moviepy.editor import *
import logging


_logger = logging.getLogger(__name__)

AMOUNT_OF_ROWS = 10


class Encoder:
    def __init__(
        self, config: GeneratorConfig, video: str,
            audio: str = './assets/videos/gaetan.mp4',
            debug: bool = False,
            debug_start: float = 0.0,
            debug_end: float = None,
            debug_step: float = 0.5,
    ) -> None:
        self.config = config
        self.base_video = video
        self.audio = audio
        self.debug = debug
        self.debug_start = float(debug_start) if debug_start else None
        self.debug_end = float(debug_end) if debug_end else None
        self.debug_step = float(debug_step) if debug_step else None

        self.audio_clip = AudioFileClip(audio)
        self.base_video_clip = VideoFileClip(self.base_video)
        if not self.debug_end:
            self.debug_end = self.base_video_clip.duration
        self.all_video_clips = []

    def encode(self):
        amount_of_pilots = len(self.config.ranking)
        for i in range(0, amount_of_pilots, 2):
            # i = 0, 2, 4, 6, 8, 10, 12, 14, 16, 18
            # idx = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
            # -> idx = (i/2) + 1
            row_index = (i//2)+1
            left_pilot_name = self.config.ranking.iloc[i][0]
            if left_pilot_name:
                left_pilot = self.config.race.get_pilot(left_pilot_name)
            else:
                left_pilot = None

            right_pilot_name = self.config.ranking.iloc[i+1][0]
            if right_pilot_name:
                right_pilot = self.config.race.get_pilot(right_pilot_name)
            else:
                right_pilot = None

            self.all_video_clips += self._encode_row(row_index, left_pilot, right_pilot)

        final = CompositeVideoClip(
            [self.base_video_clip] + self.all_video_clips,
            size=self.base_video_clip.size
        )
        # final.audio = self.audio_clip
        final = final.set_duration(self.base_video_clip.duration)

        if not self.debug:
            if self.debug_end < final.duration and self.debug_start > 0.0:
                final = final.subclip(self.debug_start, self.debug_end)
            final.write_videofile("test.mp4", fps=24)
        else:
            self._generate_frames(final)
        return self.config.output

    def _encode_row(self, index: int, left_pilot: Pilot, right_pilot: Pilot) -> List[ImageClip]:
        pilot_height = 800
        # ROW
        row_clip = ImageClip(f"./assets/grid/rows/{index}.png")
        row_duration = self._get_row_duration()
        row_clip = row_clip.set_duration(row_duration)
        row_start = self._get_row_first_frame(index)
        clips = [
            row_clip.set_position((100, 200)).set_start(row_start),
        ]
        pilot_delay = 0.3
        pilot_duration = row_duration - pilot_delay
        left_pilot_start = row_start
        right_pilot_start = row_start + pilot_delay
        # LEFT
        if left_pilot:
            # CONTENT & POSITION
            left_pilot_clip = ImageClip(left_pilot.get_celebrating_image())
            left_pilot_clip = left_pilot_clip.resize(height=pilot_height)
            left_pilot_clip = left_pilot_clip.set_position(lambda t: (320, 160))
            # DURATION & APPARITION
            left_pilot_clip = left_pilot_clip.set_start(left_pilot_start)
            left_pilot_clip = left_pilot_clip.set_duration(pilot_duration)
            left_pilot_clip = left_pilot_clip.fadein(0.5).fadeout(0.35)
            clips.append(left_pilot_clip)

        # RIGHT
        if right_pilot:
            # CONTENT & POSITION
            right_pilot_clip = ImageClip(right_pilot.get_celebrating_image())
            right_pilot_clip = right_pilot_clip.resize(height=pilot_height)
            right_pilot_clip = right_pilot_clip.set_position(lambda t: (1030, 160))

            # DURATION & APPARITION
            right_pilot_clip = right_pilot_clip.set_start(right_pilot_start)
            right_pilot_clip = right_pilot_clip.set_duration(pilot_duration)
            right_pilot_clip = right_pilot_clip.fadein(0.5).fadeout(0.35)
            clips.append(right_pilot_clip)

        return clips

    def _get_row_duration(self) -> float:
        return self._get_grid_duration() / AMOUNT_OF_ROWS

    def _get_grid_duration(self) -> float:
        # begin of grid : 33,950
        # end of grid : 65,750
        return 66.750 - self._get_grid_first_frame()

    def _get_grid_first_frame(self) -> float:
        return 33.95

    def _get_row_first_frame(self, index) -> float:
        return self._get_grid_first_frame() + (index-1) * self._get_row_duration()

    def _generate_frames(self, final: CompositeVideoClip):
        amount_of_frames = int((self.debug_end - self.debug_start) / self.debug_step)
        _logger.info(
            f'Generating {amount_of_frames} frames from {self.debug_start} to {self.debug_end} by steps of {self.debug_step}s')
        for i in range(amount_of_frames):
            timecode = self.debug_start + i*self.debug_step
            print(f'Generating {timecode}s (stopping at {self.debug_end}s)')
            final.save_frame(f'frames/{timecode}.png', t=timecode)
