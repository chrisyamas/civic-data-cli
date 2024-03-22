# Civic Data CLI Tools Repo

## About

Welcome to `civic-data-cli`, a collection of Command Line Interface (CLI) tools involving public and social sector data. This repository is a growing playground for exploring and analyzing civic data, with tools sorted into directories by sector. Whether you're a data scientist, policy analyst, or a curious citizen, this repository is intended to provide tools to access and utilize data from various sectors of public interest.

## Repository Structure & Tools Example

- **`/legis_data_tools`**: Tools for legislative data.
  - **`/usa`**: American jurisdictions.
    - **`/hi`**: Categories related to Hawaii.
      - **`/people`**: Tools for data on legislative members.
        - **`/cli_search.py`**: A script for searching that data from the command line.

### Hawaii Legislative Data CLI Search

The `cli_search.py` located in `civic-data-cli/legis_data_tools/usa/hi/people/` serves as an example of the kinds of tools added to this repository. This Python script is a CLI tool that enables users to search for information about legislators in the Hawaii State Legislature.

#### How It Works

1. **Initialization**: It starts by initializing an instance of the `HawaiiLegislature` class, which scrapes data from a specified URL containing information about Hawaii's state legislators.

2. **Data Collection and Processing**: The `process_list` method retrieves and processes the list of legislators, extracting details such as name, party, district, contact info, and social media handles.

3. **User Interaction**: The `CLIInterface` class provides an interactive command line interface where users can specify the legislative chamber (House or Senate) and district number to get information about a particular legislator.

4. **Output**: The tool then displays detailed information about the selected legislator, including name, title, party affiliation, contact details, and social media links.

5. **Interactive and User-friendly**: It includes functions for progress display, input validation, and custom messages based on the time of day.

### Contributing

This is an ongoing project which will eventually welcome contributions! For those with a tool or script that can help with the exploration of civic data, stay tuned for the `CONTRIBUTING.md` to come with guidelines on how to contribute.

### Usage

To use any of the tools in this repository:
1. Clone the repository to your local machine.
2. Navigate to the directory of the tool you're interested in.
3. Follow the specific instructions provided in the tool's directory for setup and usage.

### License

This project is licensed under the [Apache 2.0 License](LICENSE).
