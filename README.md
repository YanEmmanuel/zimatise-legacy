# Zimatise - Legacy

Zimatise is a Python-based project that streamlines the process of creating Telegram channels and uploading videos. Originally created by [apenasrr](https://github.com/apenasrr/zimatise), it is now maintained by me. With features for re-encoding videos, generating summaries, and automating the management of Telegram channels, this tool is ideal for efficiently managing large collections of videos.

## Features

- **Automated Channel Creation**: Dynamically create Telegram channels for your projects.
- **Video Processing**: Re-encode videos to specific formats and resolutions.
- **Dynamic Summaries**: Generate timestamped summaries for video content.
- **Telegram Upload Automation**: Upload videos directly to Telegram channels using Tgsender.

## In 60 Seconds of Setup

Acquire the skill to transform, for example:

- 20 GB of hundreds of videos and files

Into:

- An elegant playlist with 8 videos, 2 GB each, and interactive timestamps
- 2 independent zipped files and dynamic summary by topics
- Ready to watch and share on Telegram

Yes, in 60 seconds of setup, and highly customizable.

## Prerequisites

- **Python**: Ensure Python 3.8 or higher is installed.
- **Telegram API Credentials**: Obtain your `api_id` and `api_hash` from [Telegram API](https://my.telegram.org/).
- **Poetry**: Used for dependency management.

## Installation

Follow these steps to set up the project:

### 1. Clone the Repository

```bash
git clone https://github.com/YanEmmanuel/zimatise-lagacy.git
cd zimatise-lagacy
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Activate the Virtual Environment

```bash
poetry shell
```

## Configuration

The project requires a `config.ini` file for Telegram API credentials and other settings. Use the following template:

```ini
[default]
file_size_limit_mb = 1000
video_extensions = mp4,avi,webm,ts,vob,mov,mkv,wmv,3gp,flv,ogv,ogg,rrc,gifv,mng,qt,yuv,rm,asf,amv,m4p,m4v,mpg,mp2,mpeg,mpe,mpv,svi,3g2,mxf,roq,nsv,f4v,f4p,f4a,f4b
mode = zip
max_path = 260
duration_limit = 02:00:00.00
# activate_transition options: (false or true)
activate_transition = false
start_index = 1
hashtag_index = Block
descriptions_auto_adapt = true
document_hashtag = Doc
document_title = Documents
path_summary_top = summary_top.txt
path_summary_bot = summary_bot.txt
# reencode_plan = single or group
reencode_plan = single
silent_mode = true
create_new_channel = 1
chat_id = -100111111111
moc_chat_id = -10022222222
autodel_video_temp = 1
channel_adms =
time_limit = 99
send_moc = 0
register_invite_link = 0
# Where collections will be collected by zimatise_monitor
# Must be a folder at the root of a drive
folder_path_start = C:\z
move_to_uploaded = 0
folder_path_uploaded = C:\z_up

```

Replace `YOUR_API_ID` and `YOUR_API_HASH` with your Telegram credentials.

## Usage

### 1. Start the Project

Use the Poetry environment to run the project:

```bash
poetry run start
```

### 2. Silent Mode

The tool can be configured to operate in silent mode, processing videos and uploading them without manual intervention.

### 3. Interactive Mode

Follow the on-screen prompts to guide the processing and upload steps.

## Project Workflow

1. **Video Re-encoding**: Adjust video resolution and format as needed.
2. **Summary Generation**: Create timestamped summaries for easier navigation.
3. **Channel Creation**: Automate the creation of Telegram channels for your projects.
4. **Upload Videos**: Videos and summaries are uploaded to the designated Telegram channels.

## Additional Information

- **Last Update**: 2020-10-31
- **Original Repository**: [apenasrr/zimatise](https://github.com/apenasrr/zimatise)

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

For questions or support, please open an issue on the [GitHub repository](https://github.com/YanEmmanuel/zimatise-lagacy/issues).

