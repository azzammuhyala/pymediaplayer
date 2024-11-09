import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['PYGAME_VIDEO_HIDE_SUPPORT_PROMPT'] = '1'

from tkinter.filedialog import askopenfilename
from pyg_ui import textwrap
from pyg_ui import button

import pygvideo
import argparse
import pygame
import sys

class MediaPlayer:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description='PyMediaPlayer, video player writing in Python 3 code.')

        parser.add_argument('video_path', nargs='?', type=str, help='path to the video file')
        parser.add_argument('-l', '--loop', action='store_true', help='enable looping of the video')
        parser.add_argument('-c', '--cache', action='store_true', help='saves cache when starting the video is first loaded')
        parser.add_argument('-hs', '--hide-status', action='store_true', help='hide the status video')
        parser.add_argument('-vol', '--volume', type=float, default=1.0, help='adjust volume, default is 1')
        parser.add_argument('-fps', type=float, default=24.0, help='frames per second (FPS), default is 24')

        args = parser.parse_args()

        self.video_path = args.video_path
        self.is_loop = args.loop
        self.cache = args.cache
        self.is_hide_status = args.hide_status
        self.volume = args.volume
        self.fps = args.fps

        if self.fps < 1:
            print('[ERROR] FPS is under 1')
            sys.exit()
        elif not (0 <= self.volume <= 1):
            print('[ERROR] Volume is under 0 and above 1')
            sys.exit()

        if not self.video_path:
            self.video_path = askopenfilename(
                title='Select Video',
                filetypes=(('MP4', '*.mp4'),
                           ('MOV', '*.mov'),
                           ('AVI', '*.avi'),
                           ('MKV', '*.mkv'),
                           ('WMV', '*.wmv'),
                           ('FLV', '*.flv'),
                           ('WebM', '*.webm'))
            )
            if not self.video_path:
                print("[ERROR] No any file to play")
                sys.exit()

        pygame.init()
        pygame.mixer.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.running = True

        self.icon_path = self.resource_path('resources/assets/icons/icon.ico')
        self.roboto_regular_path = self.resource_path('resources/assets/fonts/Roboto-Regular.ttf')
        self.roboto_mono_regular_path = self.resource_path('resources/assets/fonts/RobotoMono-Regular.ttf')

        self.icon = pygame.image.load(self.icon_path)

        pygame.display.set_icon(self.icon)

        try:
            self.video = pygvideo.Video(self.video_path, has_mask=True, logger=None)
            size_video = self.video.get_clip_size()
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode((min(size_video[0], display_info.current_w - 100),
                                                   min(size_video[1], display_info.current_h - 100)),
                                                  pygame.RESIZABLE)

            self.show_preview()

        except Exception as e:
            print(f'[ERROR] {type(e).__name__}: {str(e)}')
            self.screen = pygame.display.set_mode((500, 500))
            self.show_error(e)

        finally:
            pygvideo.quit(show_log=False)
            pygame.quit()
            sys.exit()

    def resource_path(self, relative_path: os.PathLike[str]) -> os.PathLike[str]:
        try:
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath('.')

        return os.path.join(base_path, relative_path)

    def format_seconds_to_hhmmssmmm(self, milliseconds: float) -> str:
        seconds = milliseconds / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        millis = int(milliseconds % 1000)

        return f'{hours:02}:{minutes:02}:{seconds:02}.{millis:03}'

    def calculate_video_rect(self) -> pygame.Rect:
        width_screen, height_screen = self.screen.get_size()
        width_video, height_video = self.video.get_clip_size()

        scale_factor = min(width_screen / width_video, height_screen / height_video)
        new_width = int(width_video * scale_factor)
        new_height = int(height_video * scale_factor)

        return pygame.Rect((width_screen - new_width) / 2,
                           (height_screen - new_height) / 2,
                           new_width, new_height)

    def resize_screen(self, event: pygame.event.Event) -> None:
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    def generate_cache(self) -> None:
        func = self.video.iter_chunk_cache_frame()
        is_close = False

        for surf, index, ran in func:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                    is_close = True

                self.resize_screen(event)

            if is_close:
                func.send('[INFO] App closed')
                func.close()
                break

            pygame.display.set_caption(f'PyMediaPlayer - Creating Cache... ({index}/{ran.stop} frames) - {self.video_path}')

            surf_rect = self.calculate_video_rect()
            surf = pygame.transform.scale(surf, surf_rect.size)
            self.screen.blit(surf, surf_rect)

            pygame.display.flip()

    def show_preview(self) -> None:
        if self.video.get_fps() > self.fps:
            self.video.set_fps(self.fps)

        if self.cache:
            self.generate_cache()

        pygame.display.set_caption(f'PyMediaPlayer - {self.video_path}')

        button_color = {
            'normal': button.button_color('#dedede',
                                          '#c7c7c7',
                                          '#f5f5f5'),

            'active': button.button_color('#22c984',
                                          '#1bb575',
                                          '#14d987'),

            'outline': button.button_color('#8f8f8f',
                                           '#7d7d7d',
                                           '#b0b0b0')
        }

        button_color_act = lambda is_active : button_color['active' if is_active else 'normal']
        status_text = lambda : 'Show Status' if self.is_hide_status else 'Hide Status'
        status_font = pygame.font.Font(self.roboto_mono_regular_path, 15)

        status_button = button.Button(
            surface_screen=self.screen,
            id='status',
            rect=pygame.Rect(16, 0, 100, 20),
            text=status_text(),
            font=pygame.font.Font(self.roboto_regular_path, 17),
            outline_size=2,
            color=button_color_act(self.is_hide_status),
            outline_color=button_color['outline']
        )
        pause_button = status_button.copy(
            id='pause',
            rect=pygame.Rect(122, 0, 20, 20),
            text='P',
            color=button_color['normal']
        )
        mute_button = status_button.copy(
            id='mute',
            rect=pygame.Rect(148, 0, 20, 20),
            text='M',
            color=button_color['normal']
        )
        loop_button = status_button.copy(
            id='loop',
            rect=pygame.Rect(174, 0, 20, 20),
            text='L',
            color=button_color_act(self.is_loop)
        )
        slide_bar = button.Range(
            surface_screen=self.screen,
            rect=pygame.Rect(16, 0, 0, 8),
            thumb_size=(16, 16),
            outline_size=2,
            track_color=button_color['normal'],
            outline_color=button_color['outline'],
            track_fill_color=button.button_color('#427ef5',
                                                 '#1a55c9',
                                                 '#6c93e0'),
            thumb_color=button.button_color('white',
                                            'white',
                                            '#e6e6e6'),
            min_value=0,
            max_value=int(self.video.get_duration()),
            value=0,
            borders_track=button.border_radius(),
            borders_track_fill=button.border_radius()
        )

        manager = button.Manager(
            status_button,
            pause_button,
            mute_button,
            loop_button,
            slide_bar,
            inactive_cursor=pygame.SYSTEM_CURSOR_ARROW,
            active_cursor=pygame.SYSTEM_CURSOR_HAND
        )

        is_pause = False
        is_change_pos = False

        def status_video():
            self.is_hide_status = not self.is_hide_status
            status_button.text = status_text()
            status_button.color = button_color_act(self.is_hide_status)

        def pause_video():
            nonlocal is_pause
            is_pause = not is_pause
            pause_button.color = button_color_act(is_pause)
            if self.video.is_play():
                if is_pause:
                    self.video.pause()
                else:
                    self.video.unpause()
            else:
                self.video.play(self.video._Video__loops)

        def mute_video():
            if self.video.is_mute():
                self.video.unmute()
                mute_button.color = button_color['normal']
            else:
                self.video.mute()
                mute_button.color = button_color['active']

        def loop_video():
            self.is_loop = not self.is_loop
            loop_button.color = button_color_act(self.is_loop)
            if self.is_loop:
                self.video._Video__loops = -1
            else:
                self.video._Video__loops = 0

        if self.running:
            megabyte_file = self.video.get_file_size('mb')
            megabyte_file = f'~{megabyte_file:.2f}' if megabyte_file is not None else 'Unknown'

            self.video.prepare()
            self.video.set_volume(self.volume)
            self.video.play(-1 if self.is_loop else 0)

        while self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == button.BUTTON_CLICK:
                    if event.id == 'pause':
                        pause_video()
                    elif event.id == 'mute':
                        mute_video()
                    elif event.id == 'status':
                        status_video()
                    elif event.id == 'loop':
                        loop_video()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.video.add_volume(0.05)
                    elif event.key == pygame.K_DOWN:
                        self.video.sub_volume(0.05)
                    elif event.key == pygame.K_LEFT:
                        self.video.previous(5)
                    elif event.key == pygame.K_RIGHT:
                        self.video.next(5)
                    elif event.key == pygame.K_0:
                        self.video.jump(0)
                    elif event.key == pygame.K_1:
                        self.video.jump(0.1)
                    elif event.key == pygame.K_2:
                        self.video.jump(0.2)
                    elif event.key == pygame.K_3:
                        self.video.jump(0.3)
                    elif event.key == pygame.K_4:
                        self.video.jump(0.4)
                    elif event.key == pygame.K_5:
                        self.video.jump(0.5)
                    elif event.key == pygame.K_6:
                        self.video.jump(0.6)
                    elif event.key == pygame.K_7:
                        self.video.jump(0.7)
                    elif event.key == pygame.K_8:
                        self.video.jump(0.8)
                    elif event.key == pygame.K_9:
                        self.video.jump(0.9)
                    elif event.key in (pygame.K_SPACE, pygame.K_p):
                        pause_video()
                    elif event.key == pygame.K_m:
                        mute_video()
                    elif event.key == pygame.K_h:
                        status_video()
                    elif event.key == pygame.K_l:
                        loop_video()

                self.resize_screen(event)

                manager.handle_event(event)

            width_screen, height_screen = self.screen.get_size()

            video_pos = self.video.get_pos()

            slide_bar.rect.top = height_screen - 24
            slide_bar.rect.width = width_screen - 32
            pause_button.rect.top = height_screen - 51
            mute_button.rect.top = pause_button.rect.top
            loop_button.rect.top = pause_button.rect.top
            status_button.rect.top = pause_button.rect.top

            try:
                slide_bar.set_value(video_pos)
            except ValueError:
                slide_bar.set_value(slide_bar.max_value)

            video_rect = self.calculate_video_rect()

            if (size := video_rect.size) != self.video.get_size():
                self.video.set_size(size)

            self.screen.fill('black')

            frame = self.video.draw_and_update(self.screen, video_rect)

            manager.draw_and_update()

            if not self.is_hide_status:
                mouse_pos = pygame.mouse.get_pos()

                if video_rect.collidepoint(mouse_pos):
                    relative_pos = (mouse_pos[0] - video_rect.left,
                                    mouse_pos[1] - video_rect.top)
                    color = frame.get_at(relative_pos)
                    colour_str = f'(R={color[0]}, G={color[1]}, B={color[2]}, A={color[3]}, pos={mouse_pos}, relative_pos={relative_pos})'
                else:
                    colour_str = f'{mouse_pos} [NOT HOVERED]'

                if self.is_loop:
                    loop_str = f'Looping Video: {self.video.get_loops()}\n'
                else:
                    loop_str = ''

                status_surf = textwrap.render_wrap(
                    font=status_font,
                    text=f'Size Screen: (W={width_screen}, H={height_screen})\n'
                         f'Size Original Video: (W={self.video.get_original_width()}, H={self.video.get_original_height()}, size_mb={megabyte_file})\n'
                         f'Position / Total: {self.format_seconds_to_hhmmssmmm(video_pos)} / {self.format_seconds_to_hhmmssmmm(self.video.get_duration())}\n'
                         f'Position Colour: {colour_str}\n'
                         f'Frames Cache / Total: {self.video.get_total_cache_frame()} / ~{self.video.get_total_frame()}\n'
                         f'Volume: {int(self.video.get_volume() * 100)}\n'
                         f'Pause: {self.video.is_pause()}\n'
                         f'Mute: {self.video.is_mute()}\n'
                         f'{loop_str}'
                         f'FPS: (app={int(self.clock.get_fps())}, video={int(self.video.get_original_clip().fps)})',
                    wraplength=width_screen - 20,
                    antialias=True,
                    color='white',
                    background='black',
                    wrap_type='left'
                )

                status_surf.set_alpha(180)
                self.screen.blit(status_surf, (10, status_button.rect.top - 4 - status_surf.get_height()))

            if slide_bar.button_event.click:
                if not is_change_pos:
                    self.video.pause()

                self.video.set_pos(slide_bar.button_event.range_value / 1000)
                is_change_pos = True

            else:
                if is_change_pos and not is_pause:
                    self.video.unpause()
                is_change_pos = False

            pygame.display.flip()

            self.clock.tick(self.fps)

    def show_error(self, error: Exception | None = None) -> None:

        error_name = type(error).__name__

        pygame.display.set_caption(f'PyMediaPlayer - Error Unexpected: {error_name}')

        size_screen = self.screen.get_size()

        message_surf = textwrap.render_wrap(
            font=pygame.font.Font(self.roboto_regular_path, 25),
            text="Cannot play video. Corrupted video",
            wraplength=475,
            antialias=True,
            color='white',
            wrap_type='center'
        )

        if error:
            error_surf = textwrap.render_wrap(
                font=pygame.font.Font(self.roboto_mono_regular_path, 10),
                text=f'Traceback (most recent call last):\n'
                     f'  File Video {repr(self.video_path)}\n'
                     f'{error_name}: {error}',
                wraplength=500,
                antialias=True,
                color='red',
                wrap_fn='mono',
                wrap_type='left'
            )

        while self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill('black')

            self.screen.blit(message_surf, ((size_screen[0] - message_surf.get_width()) / 2, 0))

            if error:
                self.screen.blit(error_surf, (0, message_surf.get_height() + 5))

            pygame.display.flip()

            self.clock.tick(self.fps)

if __name__ == '__main__':
    MediaPlayer()