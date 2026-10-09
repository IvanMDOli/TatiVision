import os
import sys
from pathlib import Path


PLAYER_EXECUTABLES = {
    "vlc.exe": "VLC media player",
    "mpv.exe": "mpv",
    "potplayer.exe": "PotPlayer",
    "mpc-hc.exe": "Media Player Classic - Home Cinema",
    "mpc-hc64.exe": "Media Player Classic - Home Cinema",
    "mpc-be.exe": "MPC-BE",
    "mpc-be64.exe": "MPC-BE",
    "kodi.exe": "Kodi",
    "plex.exe": "Plex",
    "jellyfinmediaplayer.exe": "Jellyfin Media Player",
    "musicbee.exe": "MusicBee",
    "foobar2000.exe": "foobar2000",
    "wmplayer.exe": "Windows Media Player",
}


def _candidate_directories():
    program_files = (
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("ProgramW6432"),
        os.environ.get("LOCALAPPDATA"),
    )
    relative_directories = (
        ("VideoLAN", "VLC"),
        ("mpv",),
        ("DAUM", "PotPlayer"),
        ("K-Lite Codec Pack", "MPC-HC64"),
        ("MPC-BE x64",),
        ("Kodi",),
        ("Plex", "Plex Media Player"),
        ("Jellyfin Media Player",),
        ("MusicBee",),
        ("foobar2000",),
        ("Windows Media Player",),
    )
    for base in filter(None, program_files):
        for relative in relative_directories:
            yield Path(base, *relative)


def _registry_players():
    if sys.platform != "win32":
        return []

    import winreg

    discovered = []
    registry_roots = (
        winreg.HKEY_CURRENT_USER,
        winreg.HKEY_LOCAL_MACHINE,
    )
    registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"

    for root in registry_roots:
        try:
            with winreg.OpenKey(root, registry_path) as key:
                index = 0
                while True:
                    try:
                        executable_name = winreg.EnumKey(key, index).casefold()
                    except OSError:
                        break
                    index += 1
                    if executable_name not in PLAYER_EXECUTABLES:
                        continue

                    try:
                        with winreg.OpenKey(key, executable_name) as app_key:
                            executable_path = winreg.QueryValueEx(
                                app_key,
                                "",
                            )[0]
                    except OSError:
                        continue

                    executable_path = os.path.expandvars(
                        str(executable_path).strip().strip('"')
                    )
                    if Path(executable_path).is_file():
                        discovered.append((
                            PLAYER_EXECUTABLES[executable_name],
                            str(Path(executable_path).resolve()),
                        ))
        except OSError:
            continue

    return discovered


def discover_players():
    discovered = {}
    for name, path in _registry_players():
        normalized_path = os.path.normcase(os.path.abspath(path))
        discovered.setdefault(name.casefold(), (name, normalized_path))

    for directory in _candidate_directories():
        if not directory.is_dir():
            continue
        try:
            executables = tuple(directory.iterdir())
        except OSError:
            continue
        for executable in executables:
            name = PLAYER_EXECUTABLES.get(executable.name.casefold())
            if name and executable.is_file():
                discovered.setdefault(
                    name.casefold(),
                    (name, str(executable.resolve())),
                )

    return sorted(
        discovered.values(),
        key=lambda item: (item[0].casefold(), item[1]),
    )


def programs_directory():
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        directory = os.environ.get(variable)
        if directory and Path(directory).is_dir():
            return directory
    return str(Path.home())
