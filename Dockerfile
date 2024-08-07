FROM ghcr.io/planetarypraxis/do-app-baseimage-django-node:8955fc78fd796852180f236216c3b0bd13c06393

# Install the project requirements and build.
COPY --chown=app:app .bin/install.sh Pipfile Pipfile.lock package.json yarn.lock ./
RUN SKIP_MIGRATE=1 bash install.sh
RUN yarn

# Copy the rest of the sources over
COPY --chown=app:app . ./
ENV DJANGO_SETTINGS_MODULE=smartforests.settings.production
ENV NODE_ENV=production

# Build
RUN pipenv run bash .bin/build.sh

# Run
EXPOSE ${PORT:-8080}
