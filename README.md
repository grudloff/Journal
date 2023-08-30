# Journal Web App using Streamlit and MongoDB

This repository contains a simple web application for maintaining a personal journal. The application is built using [Streamlit](https://streamlit.io/), a Python library for creating interactive web applications, and [MongoDB](https://www.mongodb.com/), a NoSQL database. The web app allows users to add, modify, and delete journal entries, as well as filter entries based on date.

## Demo

![Personal Journal Webapp](assets/demo.gif)

## Features

- Add new journal entries.
- Modify existing journal entries.
- Delete journal entries.
- Filter entries by date range.
- Display previous journal entries.

## Getting Started

To run the journal web app locally, follow these steps:

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/journal-webapp.git
   ```

2. Install the required rependencies:

     a. Using pip. Navigate to the project directory and run:

      ```bash
      pip install -r requirements.txt
      ```

   b. Or using conda to run the code in a virtual environment. Navigate to the project directory and run:
   
      ```bash
      conda env create -f environment.yml
      ```
Then to activate the newly created environment with name "journal", run:

   ```bash
   conda activate journal
   ```
3. Ensure you have a MongoDB instance set up. You will need the connection URI which can be stored as a secret in your Streamlit Sharing account or in a `.secrets.toml` file.

4. Create a `.streamlit` directory in the root of your project (if not already present), and create a `config.toml` file inside it. Add the following lines to the `config.toml` file, replacing `<your-mongo-uri>` with your MongoDB connection URI:

   ```toml
   [secrets]
   mongo = "uri = '<your-mongo-uri>'"
   ```

5. Run the Streamlit app:

   ```bash
   streamlit run journal.py
   ```

6. The web app will open in your default web browser. You can now start adding and managing journal entries.

## Usage

- **New Entry**: Add a new journal entry by typing in the text area and clicking the "Add entry" button.

- **Filter by date**: Use the sidebar to select a start and end date to filter entries within a specific date range.

- **Number of entries**: Adjust the slider in the sidebar to select the number of entries you want to display.

- **Previous Entries**: View a list of previous journal entries based on your chosen filters.

- **Modify Entry**: Click the "Modify" button on a specific entry to edit its content. You can also delete the entry using the "Delete entry" button.

## Project Structure

- `journal.py`: The main Streamlit application script that defines the UI and interaction logic.
- `requirements.txt`: A list of required Python packages for running the web app.

## Note

- This is a simple example project and may not include advanced features such as authentication, user accounts, or extensive error handling. Ensure to enhance the app's security and reliability before deploying it to production.

- Make sure to keep your MongoDB connection string secure, especially in production environments.

## Blog Entry

I've written a blog post about the development of this journal web app. There I go into detail about using atlas MongoDB hosting and Streamlit Community Cloud to serve the webapp. Check it out for more details and insights:

[Read the blog post](https://grudloff.github.io/blog/mongodb_journal/)


## Contributing

Contributions are welcome! If you find any issues or want to add new features, feel free to create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
