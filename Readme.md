# Annotation project api

## Development setup
### Run Project

Clone the `setup` project and follow the instructions

### Select Interpreter
#### in PyCharm ...
- `Settings -> "Seach" Python interpreter -> add interpreter (Button on the right of current interpreter) -> On Docker...`
   - `Pull or use existing image`
   - Select Docker image (Probably contains flask in its name)
      - You can find it using Docker Desktop
#### in VS Code ...
Source: [dev.to](https://dev.to/alvarocavalcanti/setting-up-a-python-remote-interpreter-using-docker-1i24)
- Install the Python extension
- Install the Dev - Containers extension
- Open the Command Pallette and type `Dev-Containers`, then select the `Attach to Running Container...` and select the running docker container (flask)
- VS Code will restart and reload
- On the Explorer sidebar, click the open a folder button and then enter `/app` (this will be loaded from the remote container)
- On the Extensions sidebar, select the Python extension and install it on the container
- (When prompted on which interpreter to use, select `/usr/local/bin/python`)
- (Open the Command Palette and type Python: Configure Tests, then select the unittest framework)
### Code Formatting
- We use [Black](https://black.readthedocs.io/en/stable/index.html) to format the python code 
#### Set up in PyCharm
- install black
   - `pip install black` 
   - OR
   - `Settings -> Tools -> Black --> install black...`
- run black on save
   - `Settings -> Tools -> Actions on save --> "check" run black`
#### Set up in VS Code
- Install [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
- `Settings -> Seach "Default Formatter"`
- `Settings -> Text Editor -> Format on Save`


