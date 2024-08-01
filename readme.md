# Smart Forests Atlas

A tool to capture and narrate smart forests data, including fieldwork, interviews, social network analysis, maps and environmental data from instrumented forests.

See the live site at https://atlas.smartforests.net

## Development

### Requirements
- Docker Desktop
- VSCode
- VSCode [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension 


### Process
- Clone the repository from https://github.com/planetarypraxis/smartforests
- Open the repository folder in VSCode
- You should get a notification asking if you want to 'reopen in container'. Say yes.
  - If you don't get one, you should be able to 'reopen in container' via the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette)
  - If you can't see an option to do that, make sure you have the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension  installed
- Wait for the dev container to build.
- Check your [VSCode terminal](https://code.visualstudio.com/docs/terminal/basics) and respond to any setup prompts it asks for
- Copy the settings from [Bitwarden](https://vault.bitwarden.com/) into [smartforests/settings/local.py](smartforests/settings/local.py)
- Use the VSCode [run and debug view](https://code.visualstudio.com/docs/editor/debugging#_run-and-debug-view) (should appear if you press F5 on your keyboard) to run the app.
  - Make sure you use the 'App' configuration, which will start both the django app and the frontend build pipeline.
  - The `setup_pages` command in `manage.py` will set up the basic page structure in the development site.
- To import the production database 
- Go to [localhost:8000/admin](http://localhost:8000/admin) for the CMS
- Go [localhost:8000](http://localhost:8000)


### Issues
- (Optional: if necessary) Make sure VSCode has selected the correct python interpreter ('command palette > Python: Select Interpreter'). It should be set to the Python in the virtualenv (venv).
 

## Other Technical documentation

### Build / deployment process

This repository has a development dockerfile (.devcontainer/Dockerfile) and a production one (./Dockerfile).

They both run .bin in ./.bin to configure their environments and install dependencies:

- Base container configuration, which is run infrequently (installing apt packages, etc) should be configured in prepare.sh.
- Frequently-run .bin (installing pip packages, etc) should go in install.sh. The difference between these is that changing prepare.sh triggers a full rebuild of the development container, whereas install.sh is only run after the container is built.
- `build.sh` is the last thing run on deploy to production

### Regenerating tag clouds and re-indexing logbooks

Producing tag clouds is a relatively computationally intensive operation, so we do it only occasionally with a Django management command.

```
python manage.py reindex_logbooks
```

This command:
- Saves all pages in order to update their location.
- Regenerates thumbnails for logbooks.
- Generates tag clouds.
- Creates a contributor page for each user.

You should run this command if you modify the save behaviour of models, or change the tag cloud generation algorithm.

### Background tasks to regenerate tag clouds

Tag clouds are also generated with a [background task](https://github.com/planetarypraxis/smartforests/blob/main/logbooks/tasks.py) using [django-background-tasks](https://django-background-tasks.readthedocs.io/en/latest/). This task is run 15 seconds [after a tag is saved](https://github.com/planetarypraxis/smartforests/blob/f6efb6a1ed87433df9d3d4c15e60afef34a5f310/logbooks/models/snippets.py#L21-L25). 

Reindexing all tags takes around 30 minutes.

### Translations

1. To (re)generate the message files (.po), run `yarn makemessages` or `python manage.py makemessages --locale=pt --locale=es --locale=fr --extension=html --ignore=env/**/*`
2. We use [django-deep-translate](https://pypi.org/project/django-deep-translator/) to automatically translate the message files. Ensure `DEEPL_TRANSLATE_KEY` is set in [`smartforests/settings/local.py`](./smartforests/settings/local.py) then run `python manage.py translate_messages`
3. After translation, you must compile the message files using `django-admin compilemessages`


## Stack

- Django (fullstack django app, no js frontend)
- Bootstrap (css an' stuff)
- Wagtail (CMS, administration, editor workflows and storage)
- Webpack (asset pipeline)
- PostgreSQL (Database & search index)

## Hosting

- Digital Ocean (production)
- Fly.io (staging)

## Third party services

- Digital Ocean App Platform (Compute, database hosting, object storage & CDN)
- Mapbox
