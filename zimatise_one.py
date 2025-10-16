from __future__ import annotations
import logging
import os
from pathlib import Path
import vidtool
import zipind
from tgsender import tgsender
import autopost_summary
import project_metadata
import update_description_summary
import utils
from description import single_mode
from header_maker import header_maker
from timestamp_link_maker import timestamp_link_maker, utils_timestamp


def logging_config():
    logfilename = "log-zimatise.txt"
    logging.basicConfig(
        level=logging.INFO,
        format=" %(asctime)s-%(levelname)s-%(message)s",
        handlers=[logging.FileHandler(logfilename, "w", "utf-8")],
    )
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def menu_ask():
    options = [
        "1-Create independent Zip parts for not_video_files",
        "2-Generate worksheet listing the files",
        "3-Process reencode of videos marked in column \"video_resolution_to_change\"",
        "4-Group videos with the same codec and resolution",
        "5-Make Timestamps and Descriptions report",
        "6-Auto-send to Telegram"
    ]
    
    for option in options:
        print(option)
    
    try:
        choice = int(input("\nType your answer: "))
        if 1 <= choice <= 6:
            return choice
        else:
            raise ValueError("Invalid option")
    except (ValueError, IndexError):
        raise ValueError("Invalid option")


def play_sound():
    os.system('start wmplayer ""')


def define_mb_per_file(file_path_config, file_size_limit_mb):
    if file_size_limit_mb is not None:
        repeat_size = input(f"Define limit of {file_size_limit_mb} MB per file? y/n\n")
        if repeat_size == "n":
            file_size_limit_mb = zipind.zipind.ask_mb_file()
            zipind.zipind.config_update_data(file_path_config, "file_size_limit_mb", str(file_size_limit_mb))
    else:
        file_size_limit_mb = zipind.zipind.ask_mb_file()
        zipind.zipind.config_update_data(file_path_config, "file_size_limit_mb", str(file_size_limit_mb))
    return file_size_limit_mb


def run_silent_mode(folder_path_project, file_path_report, list_video_extensions, file_size_limit_mb,
                    duration_limit, start_index, activate_transition, hashtag_index, dict_summary,
                    descriptions_auto_adapt, path_summary_top, document_hashtag, document_title,
                    register_invite_link, reencode_plan, mode, config_data):
    
    folder_path_project = vidtool.get_folder_path(folder_path_project)
    file_path_report = vidtool.set_path_file_report(folder_path_project)
    folder_path_report = file_path_report.parent
    folder_path_output = folder_path_report / "output_videos"

    utils.ensure_folder_existence([folder_path_output])
    zipind.zipind_core.run(
        path_folder=folder_path_project,
        mb_per_file=file_size_limit_mb,
        path_folder_output=folder_path_output,
        mode=mode,
        ignore_extensions=list_video_extensions,
    )

    vidtool.step_create_report_filled(folder_path_project, file_path_report, list_video_extensions, reencode_plan)
    
    folder_path_videos_encoded = vidtool.set_path_folder_videos_encoded(folder_path_project)
    vidtool.ensure_folder_existence([folder_path_videos_encoded])
    vidtool.set_make_reencode(file_path_report, folder_path_videos_encoded)

    folder_path_videos_splitted = vidtool.set_path_folder_videos_splitted(folder_path_project)
    folder_path_videos_joined = vidtool.set_path_folder_videos_joined(folder_path_project)
    folder_path_videos_cache = vidtool.set_path_folder_videos_cache(folder_path_project)
    
    vidtool.ensure_folder_existence([folder_path_videos_splitted, folder_path_videos_joined, folder_path_videos_cache])
    
    filename_output = vidtool.get_folder_name_normalized(folder_path_project)

    if reencode_plan == "group":
        vidtool.set_group_column(file_path_report)

    vidtool.set_split_videos(file_path_report, file_size_limit_mb, folder_path_videos_splitted, duration_limit)

    if reencode_plan == "group":
        vidtool.set_join_videos(file_path_report, file_size_limit_mb, filename_output, folder_path_videos_joined,
                               folder_path_videos_cache, duration_limit, start_index, activate_transition)

    if reencode_plan == "group":
        timestamp_link_maker(folder_path_output=folder_path_report, file_path_report_origin=file_path_report,
                            hashtag_index=hashtag_index, start_index_number=start_index, dict_summary=dict_summary,
                            descriptions_auto_adapt=descriptions_auto_adapt)
        update_description_summary.main(path_summary_top, folder_path_report, document_hashtag, document_title)
    else:
        single_mode.single_description_summary(folder_path_output=folder_path_report,
                                              file_path_report_origin=file_path_report, dict_summary=dict_summary)
        update_description_summary.main(path_summary_top, folder_path_report, document_hashtag, document_title)

    header_maker(folder_path_report, folder_path_project)

    has_warning = utils_timestamp.check_descriptions_warning(folder_path_report)
    if has_warning:
        input('\nThere are warnings in the file "descriptions.xlsx". Correct before the next step.')

    print(f"\nProject: {folder_path_report}\n")
    tgsender.send_via_telegram_api(Path(folder_path_report), config_data)
    autopost_summary.run(folder_path_report)

    if register_invite_link == "1":
        project_metadata.include(folder_path_project, folder_path_report)

    utils.move_project(folder_path_project, config_data)


def main():
    folder_script_path = utils.get_folder_script_path()
    file_path_config = folder_script_path / "config.ini"
    config_data = utils.get_config_data(file_path_config)
    file_size_limit_mb = int(config_data["file_size_limit_mb"])
    mode = config_data["mode"]
    max_path = int(config_data["max_path"])
    list_video_extensions = config_data["video_extensions"].split(",")
    duration_limit = config_data["duration_limit"]
    activate_transition = config_data["activate_transition"]
    start_index = int(config_data["start_index"])
    hashtag_index = config_data["hashtag_index"]
    reencode_plan = config_data["reencode_plan"]
    descriptions_auto_adapt = config_data["descriptions_auto_adapt"] == "true"
    silent_mode = config_data["silent_mode"] == "true"

    path_summary_top = Path("user") / config_data["path_summary_top"]
    path_summary_bot = Path("user") / config_data["path_summary_bot"]
    document_hashtag = config_data["document_hashtag"]
    document_title = config_data["document_title"]
    register_invite_link = config_data["register_invite_link"]

    dict_summary = {
        "path_summary_top": path_summary_top,
        "path_summary_bot": path_summary_bot
    }
    
    file_path_report = None
    folder_path_project = None
    utils.ensure_folder_existence([Path("projects")])

    if silent_mode:
        while True:
            ensure_silent_mode = input("Continue to silent mode? (y/n) ")
            if ensure_silent_mode != "y" and ensure_silent_mode != "":
                break
            run_silent_mode(
                folder_path_project,
                file_path_report,
                list_video_extensions,
                file_size_limit_mb,
                duration_limit,
                start_index,
                activate_transition,
                hashtag_index,
                dict_summary,
                descriptions_auto_adapt,
                path_summary_top,
                document_hashtag,
                document_title,
                register_invite_link,
                reencode_plan,
                mode,
                config_data,
            )
            input("\nProject processed and sent to Telegram")
            vidtool.clean_cmd()

    while True:
        menu_answer = menu_ask()

        if menu_answer == 1:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(folder_path_project)
            folder_path_report = file_path_report.parent

            if not folder_path_project.exists():
                input("\nThe folder does not exist.")
                vidtool.clean_cmd()
                continue

            file_size_limit_mb = define_mb_per_file(file_path_config, file_size_limit_mb)

            if not zipind.zipind.ensure_folder_sanitize(folder_path_project, max_path):
                vidtool.clean_cmd()
                continue

            folder_path_output = folder_path_report / "output_videos"
            utils.ensure_folder_existence([folder_path_output])
            zipind.zipind_core.run(
                path_folder=folder_path_project,
                mb_per_file=file_size_limit_mb,
                path_folder_output=folder_path_output,
                mode=mode,
                ignore_extensions=list_video_extensions,
            )
            input("\nZip files created.")
            vidtool.clean_cmd()
            continue

        elif menu_answer == 2:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(folder_path_project)

            vidtool.step_create_report_filled(folder_path_project, file_path_report, list_video_extensions, reencode_plan)

            print('\nIf necessary, change the reencode plan in the column "video_resolution_to_change"')
            input("Type Enter to continue")
            vidtool.clean_cmd()
            continue

        elif menu_answer == 3:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(folder_path_project)
            folder_path_videos_encoded = vidtool.set_path_folder_videos_encoded(folder_path_project)
            vidtool.ensure_folder_existence([folder_path_videos_encoded])

            vidtool.set_make_reencode(file_path_report, folder_path_videos_encoded)

            if reencode_plan == "group":
                print("start correcting the duration metadata")
                vidtool.set_correct_duration(file_path_report)
                print("Duration metadata corrected.")
            
            input('Type something to go to the main menu, and proceed to the "Group videos" process.')
            vidtool.clean_cmd()
            continue

        elif menu_answer == 4:
            print("DEBUG: Starting menu option 4")
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            print(f"DEBUG: Got folder path: {folder_path_project}")
            
            file_path_report = vidtool.set_path_file_report(folder_path_project)
            print(f"DEBUG: Got report path: {file_path_report}")
            
            folder_path_videos_splitted = vidtool.set_path_folder_videos_splitted(folder_path_project)
            folder_path_videos_joined = vidtool.set_path_folder_videos_joined(folder_path_project)
            folder_path_videos_cache = vidtool.set_path_folder_videos_cache(folder_path_project)
            print("DEBUG: Got all folder paths")
            
            vidtool.ensure_folder_existence([folder_path_videos_splitted, folder_path_videos_joined, folder_path_videos_cache])
            print("DEBUG: Ensured folder existence")
            
            filename_output = vidtool.get_folder_name_normalized(folder_path_project)
            print(f"DEBUG: Got filename output: {filename_output}")

            print("DEBUG: Checking if join process has started...")
            if not vidtool.join_process_has_started(file_path_report):
                print("DEBUG: Join process has not started")
                if reencode_plan == "group":
                    print("DEBUG: Setting group column...")
                    vidtool.set_group_column(file_path_report)
                    print("DEBUG: Group column set")
                    input("Review the file and then type something to start the process that look for videos that are too big and should be splitted")

                print("DEBUG: Starting split videos...")
                vidtool.set_split_videos(file_path_report, file_size_limit_mb, folder_path_videos_splitted, duration_limit)
                print("DEBUG: Split videos completed")
            else:
                print("DEBUG: Join process has already started")

            print("DEBUG: Checking reencode plan...")
            if reencode_plan == "group":
                print("DEBUG: Starting join videos...")
                vidtool.set_join_videos(file_path_report, file_size_limit_mb, filename_output, folder_path_videos_joined,
                                       folder_path_videos_cache, duration_limit, start_index, activate_transition)
                print("\nAll videos were grouped")
            
            input('Go to the "Make Time Stamps" step.')
            vidtool.clean_cmd()
            continue

        elif menu_answer == 5:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(folder_path_project)
            folder_path_report = file_path_report.parent

            if reencode_plan == "group":
                timestamp_link_maker(folder_path_output=folder_path_report, file_path_report_origin=file_path_report,
                                    hashtag_index=hashtag_index, start_index_number=start_index, dict_summary=dict_summary,
                                    descriptions_auto_adapt=descriptions_auto_adapt)
                update_description_summary.main(path_summary_top, folder_path_report, document_hashtag, document_title)
            else:
                single_mode.single_description_summary(folder_path_output=folder_path_report,
                                                      file_path_report_origin=file_path_report, dict_summary=dict_summary)
                update_description_summary.main(path_summary_top, folder_path_report, document_hashtag, document_title)

            header_maker(folder_path_report, folder_path_project)
            print("\nTimeStamp and descriptions files created.")

            has_warning = utils_timestamp.check_descriptions_warning(folder_path_report)
            if has_warning:
                input('\nThere are warnings in the file "descriptions.xlsx". Correct before the next step.')
            else:
                input("\nType something to go to the main menu")
            vidtool.clean_cmd()
            continue

        elif menu_answer == 6:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(folder_path_project)
            folder_path_report = file_path_report.parent

            print(f"\nProject: {folder_path_report}\n")
            tgsender.send_via_telegram_api(Path(folder_path_report), config_data)
            autopost_summary.run(folder_path_report)

            if register_invite_link == "1":
                project_metadata.include(folder_path_project, folder_path_report)

            input("All files were sent to the telegram")
            vidtool.clean_cmd()
            utils.move_project(folder_path_project, config_data)
            return


if __name__ == "__main__":
    logging_config()
    main()