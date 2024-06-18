import os
import subprocess
from collections import defaultdict

from dsutil.progress import halo_progress_context
from dsutil.text import color, print_colored


def _run_ffmpeg_command(command: list[str], input_file: str, show_output: bool) -> None:
    """
    Run a given ffmpeg command and handle progress display and errors.

    Args:
        command: The ffmpeg command to execute.
        input_file: The path to the input file.
        show_output: Whether to display output.
    """
    spinner_messages = {
        "start": "Converting",
        "end": "Converted",
        "fail": "Failed to convert",
    }

    with halo_progress_context(
        filename=os.path.basename(input_file),
        start_message=spinner_messages["start"],
        end_message=spinner_messages["end"],
        fail_message=spinner_messages["fail"],
        show=show_output,
    ) as spinner:
        try:
            subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            error_message = f"Error converting file '{input_file}'. Command '{' '.join(command)}' exited with status {e.returncode}. Error output:\n{e.stderr}"
            if spinner is not None:
                spinner.fail(color(error_message, "red"))
            else:
                print_colored(error_message, "red")
            raise RuntimeError(error_message) from e
        except Exception as e:
            if spinner is not None:
                spinner.fail(color(f"Unexpected error: {e}", "red"))
            else:
                print_colored(f"Unexpected error: {e}", "red")
            raise


def _generate_output_filename(
    input_file: str, output_file: str, output_format: str, input_files: list[str]
) -> str:
    """
    Generate the output file name based on the input file and the output format.

    Args:
        input_file: The path to the input file.
        output_file: The path to the output file. Defaults to None.
        output_format: The desired output format.
        input_files: A list of input files.

    Returns:
        str: The output file name.
    """
    if not output_file:
        return f"{os.path.splitext(input_file)[0]}.{output_format}"
    return (
        output_file
        if len(input_files) == 1
        else f"{os.path.splitext(output_file)[0]}_{os.path.basename(input_file)}{os.path.splitext(output_file)[1]}"
    )


def _construct_base_command(input_file: str, overwrite: bool) -> list[str]:
    """
    Construct the base ffmpeg command.

    Args:
        input_file: The path to the input file.
        overwrite: Whether to overwrite the output file if it already exists.
    """
    command = ["ffmpeg"]
    if overwrite:
        command += ["-y"]
    command += [
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_file,
    ]
    return command


def _apply_codec_settings_for_audio(
    command: list[str], codec: str, output_format: str, audio_bitrate: str, sample_rate: str, bit_depth: int
) -> None:
    """
    Apply the codec settings to the ffmpeg command for audio conversion.

    Args:
        command: The ffmpeg command to which to apply the settings.
        codec: The desired codec. Defaults to None.
        output_format: The desired output format.
        audio_bitrate: The desired audio bitrate. Defaults to None.
        sample_rate: The desired sample rate. Defaults to None.
        bit_depth: The desired bit depth. Defaults to 16.
    """
    if output_format == "m4a" and not codec:
        codec = "alac"
    command += ["-vn"]
    if codec:
        command += ["-acodec", codec]
    else:
        codec_to_format = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "flac": "flac",
        }
        command += ["-acodec", codec_to_format.get(output_format, "copy")]

    if audio_bitrate:
        command += ["-b:a", audio_bitrate]

    if sample_rate:
        command += ["-ar", sample_rate]

    if (
        codec in {"pcm_s16le", "pcm_s24le", "pcm_s32le"}
        or bit_depth in {16, 24, 32}
        and output_format in {"wav", "flac"}
    ):
        sample_format_mappings = {
            16: "s16",
            24: "s24",
            32: "s32",
        }
        sample_format = sample_format_mappings.get(bit_depth, "s16")
        command += ["-sample_fmt", sample_format]


def _apply_codec_settings_for_video(
    command: list[str], video_codec: str, video_bitrate: str, audio_codec: str
) -> None:
    """
    Apply the codec settings to the ffmpeg command for video conversion.

    Args:
        command: The ffmpeg command to which to apply the settings.
        video_codec: The desired video codec. Defaults to None.
        video_bitrate: The desired video bitrate. Defaults to None.
        audio_codec: The desired audio codec. Defaults to None.
    """
    command += ["-c:v", video_codec] if video_codec else ["-c:v", "copy"]
    if video_bitrate:
        command += ["-b:v", video_bitrate]

    command += ["-c:a", audio_codec] if audio_codec else ["-c:a", "copy"]


def _prioritize_lossless_audio_formats(input_files: list[str]) -> list:
    """
    If there are multiple files with the same name, this function will sort the list such
    that uncompressed and lossless files are prioritized over compressed and lossy files.

    Args:
        input_files: A list of input files.
    """
    file_groups = defaultdict(list)

    for file in input_files:
        file_str = str(file)
        base_name = os.path.splitext(os.path.basename(file_str))[0]
        file_groups[base_name].append(file_str)

    prioritized_extensions = [".wav", ".aiff", ".aif", ".flac", ".m4a"]

    prioritized_files = []
    for _, files in file_groups.items():
        selected_file = None
        for ext in prioritized_extensions:
            for file in files:
                if file.lower().endswith(ext):
                    selected_file = file
                    break
            if selected_file:
                break
        if not selected_file:
            selected_file = files[0]
        prioritized_files.append(selected_file)
    return prioritized_files
