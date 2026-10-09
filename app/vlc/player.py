import os
import subprocess

from config.user_settings import get_user_setting


def play_video(video_path):
    if not os.path.isfile(video_path):
        raise FileNotFoundError(
            f"No se encontró el archivo de video: {video_path}"
        )

    player_mode = get_user_setting("player_mode")
    if player_mode == "system":
        os.startfile(video_path)
        return

    if player_mode == "custom":
        player_path = get_user_setting("custom_player_path")
        if not player_path or not os.path.isfile(player_path):
            raise FileNotFoundError(
                "El reproductor configurado ya no está disponible. "
                "Elegí otro desde Ajustes."
            )
        subprocess.Popen(
            [os.path.abspath(player_path), os.path.abspath(video_path)]
        )
        return

    raise RuntimeError(
        f"El modo de reproducción configurado no es válido: {player_mode}"
    )


def play_movie(video_path):
    play_video(video_path)